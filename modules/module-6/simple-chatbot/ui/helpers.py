import json
import json
import streamlit as st

from streaming_types import OpenAIResponseAPIStreamingState
from logger import ChatbotLogger



logger = ChatbotLogger.get_logger("streamlit_handlers")



def load_json_schema() -> dict | None:
    """
    Handle JSON schema upload and parsing
    
    Returns:
        Parsed schema dict or None
    """
    json_file = st.file_uploader(
        "Tải lên file lược đồ (JSON)",
        type=["json"],
    )
    
    if json_file is not None:
        try:
            file_content = json_file.read().decode("utf-8")
            output_schema = json.loads(file_content)
            schema_display = json.dumps(output_schema, ensure_ascii=False, indent=2)
            st.success("Đọc lược đồ từ file JSON thành công!")
            st.code(schema_display, language="json")
            return output_schema
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse JSON file: {e}")
            st.error("Không đọc được file JSON. Vui lòng kiểm tra lại nội dung.")
            return None
    return None



def parse_json_schema_text(schema_text: str) -> dict | None:
    """
    Parse JSON schema from text input
    
    Args:
        schema_text: JSON string
        
    Returns:
        Parsed schema dict or None
    """
    try:
        output_schema = json.loads(schema_text)
        st.success("Lược đồ hợp lệ!")
        return output_schema
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON schema: {e}")
        st.error("Định dạng JSON không hợp lệ. Vui lòng kiểm tra lại.")
        return None



def disable_streaming_when_structured() -> None:
    """Disable the streaming checkbox if structured output is enabled.

    Intended to be used as an `on_change` callback for the structured
    format checkbox in the Streamlit UI.
    """
    try:
        if st.session_state.get("structured_mode_widget", False):
            st.session_state["streaming_mode_widget"] = False
    except Exception as e:
        logger.debug(f"Failed to disable streaming widget: {e}")



def display_streaming_response(response_generator) -> dict | None:
    """Consume a streaming response and render it incrementally.

    Returns a dict suitable for appending to `chat_history` when the stream completes.
    """
    # Keep text streaming incrementally; reasoning will render once at the end.
    # Placeholder order controls visual order in Streamlit: reasoning above text.
    reasoning_tool_placeholder = st.empty()
    content_placeholder = st.empty()
    reasoning_tool_content_response = ""
    reasoning_tool_final_response = ""
    content_response = ""
    tool_call_trace: list[dict[str, object]] = []

    for event in response_generator:
        # event.type can be one of our enum values
        etype = getattr(event, "type", None)

        match etype:
            case (
                OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DELTA
                | OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DELTA
            ):
                delta = getattr(event, "delta", "")
                if delta:
                    reasoning_tool_content_response += delta
                    # Update the reasoning placeholder live so the UI shows
                    # intermediate reasoning while streaming. Show the
                    # reasoning text first, then the tool call list.
                    if reasoning_tool_content_response or tool_call_trace:
                        with reasoning_tool_placeholder.expander("PROCESSING", expanded=True):
                            if reasoning_tool_content_response:
                                st.markdown(reasoning_tool_content_response)
                            if tool_call_trace:
                                st.markdown("**Các công cụ đã gọi:**")
                                for call in tool_call_trace:
                                    args = call.get("arguments", {})
                                    args_text = json.dumps(args, ensure_ascii=False, indent=2) if args else "{}"
                                    st.markdown(f"- **{call.get('name', 'Không rõ')}**")
                                    st.code(args_text, language="json")

            case (
                OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DONE
                | OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DONE
                | OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_ITEM_DONE
            ):
                # Prefer final reasoning payload when available.
                done_text = getattr(event, "text", "")
                if done_text:
                    reasoning_tool_final_response = done_text

                # Capture tool call details from output items when present.
                item = getattr(event, "item", None) or getattr(event, "output_item", None)
                if item:
                    item_type = getattr(item, "type", None)
                    if item_type in ("function_call", "tool_call"):
                        raw_args = getattr(item, "arguments", None)
                        try:
                            parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                            if parsed_args is None:
                                parsed_args = {}
                        except Exception:
                            parsed_args = {"_raw": raw_args}

                        tool_call_trace.append({
                            "name": getattr(item, "name", ""),
                            "arguments": parsed_args,
                        })

                # Update reasoning placeholder when a tool call completes or
                # when final reasoning text arrives so the UI reflects progress.
                if reasoning_tool_final_response or tool_call_trace:
                    with reasoning_tool_placeholder.expander("REASONING", expanded=True):
                        if reasoning_tool_final_response:
                            st.markdown(reasoning_tool_final_response)
                        if tool_call_trace:
                            st.markdown("**Các công cụ đã gọi:**")
                            for call in tool_call_trace:
                                args = call.get("arguments", {})
                                args_text = json.dumps(args, ensure_ascii=False, indent=2) if args else "{}"
                                st.markdown(f"- **{call.get('name', 'Không rõ')}**")
                                st.code(args_text, language="json")

            case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DELTA:
                delta = getattr(event, "delta", "")
                if delta:
                    content_response += delta
                    content_placeholder.markdown(content_response)

            case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DONE:
                done_text = getattr(event, "text", "")
                if done_text:
                    content_response = done_text

            case OpenAIResponseAPIStreamingState.RESPONSE_COMPLETED:
                # Do not stop on intermediate completion events; tool flows
                # can emit additional cycles with the final assistant text.
                continue

    final_reasoning = reasoning_tool_final_response.strip()
    if final_reasoning or tool_call_trace:
        with reasoning_tool_placeholder.expander("REASONING", expanded=True):
            if final_reasoning:
                st.markdown(final_reasoning)
            if tool_call_trace:
                st.markdown("**Các công cụ đã gọi:**")
                for call in tool_call_trace:
                    args = call.get("arguments", {})
                    args_text = json.dumps(args, ensure_ascii=False, indent=2) if args else "{}"
                    st.markdown(f"- **{call.get('name', 'Không rõ')}**")
                    st.code(args_text, language="json")

    # Build assistant message dict to append to history
    message = {"role": "assistant"}
    if final_reasoning:
        message["reasoning_content"] = final_reasoning
    if content_response:
        message["content"] = content_response
    if tool_call_trace:
        message["tool_trace"] = tool_call_trace

    # Remember whether this assistant message should show the REASONING
    # expander open by default. We keep it open for messages that include
    # reasoning text or tool calls; it will be collapsed on the next user
    # input via the app-level session flag.
    message["expand_reasoning"] = bool(final_reasoning or tool_call_trace)

    return message



def enforce_mutual_exclusion(active_key: str, inactive_key: str) -> None:
    """When a widget with key `active_key` becomes True, ensure
    the widget with key `inactive_key` is set to False.

    This function uses `st.session_state` and is intended to be used
    as an `on_change` callback for checkboxes in the Streamlit UI.
    """
    try:
        if st.session_state.get(active_key, False):
            st.session_state[inactive_key] = False
    except Exception as e:
        logger.debug(f"Failed to enforce mutual exclusion: {e}")



def render_chat_history(chat_history: list[dict[str, str]]) -> None:
    """
    Render chat history in Streamlit
    
    Args:
        chat_history: List of chat messages
    """
    for msg in chat_history:
        role = msg.get("role", "user")
        reasoning = msg.get("reasoning_content", "")
        content = msg.get("content", "")
        
        tool_trace = msg.get("tool_trace", [])
        with st.chat_message(role):
            if reasoning or tool_trace:
                # Determine whether the expander should be open. The app sets
                # `collapse_reasoning` in session state when the user submits a
                # new message to collapse previous reasoning boxes.
                collapse_all = st.session_state.get("collapse_reasoning", False)
                expanded = msg.get("expand_reasoning", False) and not collapse_all
                with st.expander("REASONING", expanded=expanded):
                    if reasoning:
                        st.markdown(reasoning)
                    if tool_trace:
                        st.markdown("**Các công cụ đã gọi:**")
                        for call in tool_trace:
                            args = call.get("arguments", {})
                            args_text = json.dumps(args, ensure_ascii=False, indent=2) if args else "{}"
                            st.markdown(f"- **{call.get('name', 'Không rõ')}**")
                            st.code(args_text, language="json")
            if content.startswith("{") and content.endswith("}"):
                json_data = json.loads(content)
                st.json(json_data)
            else:
                st.markdown(content)