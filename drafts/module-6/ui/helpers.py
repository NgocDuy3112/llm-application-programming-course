import json
import uuid
import streamlit as st

from streaming_types import OpenAIResponseAPIStreamingState
from logger import ChatbotLogger



logger = ChatbotLogger.get_logger("streamlit_handlers")


def _normalize_tool_args(raw_arguments: object) -> dict:
    """Best-effort parse tool arguments into a dict for UI rendering."""
    try:
        parsed_args = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
        if parsed_args is None:
            return {}
        if isinstance(parsed_args, dict):
            return parsed_args
        return {"_value": parsed_args}
    except Exception:
        return {"_raw": raw_arguments}




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
    assistant_placeholder = st.empty()
    reasoning_content_response = ""
    content_response = ""
    tool_calls = []

    # processing_items is the timeline of items shown inside the
    # PROCESSING expander. Each item is a dict { type: 'reasoning'|'tool',
    # content: str, meta: dict }
    processing_items: list[dict] = []
    _processing_expander_created = False
    _processing_area_placeholder = None

    with assistant_placeholder.container():
        with st.chat_message("assistant"):
            content_placeholder = st.empty()

            def ensure_processing_area():
                nonlocal _processing_expander_created, _processing_area_placeholder
                if not _processing_expander_created:
                    with st.expander("PROCESSING"):
                        _processing_area_placeholder = st.empty()
                    _processing_expander_created = True

            def render_processing():
                """Render the ordered processing_items into the expander placeholder."""
                if not _processing_expander_created or _processing_area_placeholder is None:
                    return
                rendered = []
                for item in processing_items:
                    if item.get("type") == "reasoning":
                        # reasoning content may be multi-line markdown
                        rendered.append(item.get("content", ""))
                    elif item.get("type") == "tool":
                        meta = item.get("meta", {})
                        # Only support function_call_output schema; show tool name and args
                        tool_name = meta.get("name")
                        args = meta.get("arguments", {}) or {}
                        args_text = json.dumps(args, ensure_ascii=False) if args else "{}"
                        if tool_name:
                            header = f"**`{tool_name}({args_text})`**"
                        else:
                            header = f"**`function_call_output({args_text})`**"
                        rendered.append(header)
                        output = meta.get("output", "")
                        if output:
                            rendered.append(f"```\n{output}\n```")

                _processing_area_placeholder.markdown("\n\n".join(rendered), unsafe_allow_html=True)

            def _ensure_current_reasoning_item() -> dict:
                # Return the last reasoning item or create a new one.
                if processing_items and processing_items[-1].get("type") == "reasoning":
                    return processing_items[-1]
                item = {"type": "reasoning", "content": "", "meta": {}}
                processing_items.append(item)
                return item

            for event in response_generator:
                etype = getattr(event, "type", None)

                match etype:
                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DELTA:
                        delta = getattr(event, "delta", "")
                        if delta:
                            cur = _ensure_current_reasoning_item()
                            cur["content"] += delta
                            reasoning_content_response += delta
                            ensure_processing_area()
                            render_processing()

                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DELTA:
                        delta = getattr(event, "delta", "")
                        if delta:
                            cur = _ensure_current_reasoning_item()
                            cur["content"] += delta
                            reasoning_content_response += delta
                            ensure_processing_area()
                            render_processing()

                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DONE:
                        done_text = getattr(event, "text", "")
                        if done_text:
                            cur = _ensure_current_reasoning_item()
                            cur["content"] = done_text
                            reasoning_content_response = done_text
                            ensure_processing_area()
                            render_processing()

                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DONE:
                        done_text = getattr(event, "text", "")
                        if done_text:
                            cur = _ensure_current_reasoning_item()
                            cur["content"] = done_text
                            reasoning_content_response = done_text
                            ensure_processing_area()
                            render_processing()

                    case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_ITEM_DONE:
                        item = getattr(event, "item", None) or getattr(event, "output_item", None)
                        if not item:
                            continue

                        item_type = getattr(item, "type", None)
                        # Detection event: the model asked to call a tool/function
                        if item_type in ("function_call", "tool_call"):
                            call_id = getattr(item, "call_id", None) or getattr(item, "id", None)
                            if not call_id:
                                call_id = str(uuid.uuid4())

                            # Parse arguments for display
                            raw_args = (
                                getattr(item, "arguments", None)
                                or getattr(item, "input", None)
                                or getattr(item, "tool_input", None)
                            )
                            parsed_args = _normalize_tool_args(raw_args)

                            # Extract tool name if present
                            tool_name = getattr(item, "name", None) or getattr(item, "function_name", None) or getattr(item, "tool_name", None)

                            # Append a function_call_output placeholder (output will be
                            # filled by the service later; UI shows a header + optional output).
                            tool_calls.append({
                                "type": "function_call_output",
                                "call_id": call_id,
                                "name": tool_name,
                                "arguments": parsed_args,
                                "output": "",
                            })

                            # insert a tool item into the processing timeline
                            processing_items.append({
                                "type": "tool",
                                "content": "",
                                "meta": {"type": "function_call_output", "call_id": call_id, "name": tool_name, "arguments": parsed_args, "output": ""},
                            })
                            ensure_processing_area()
                            render_processing()

                        # Tool output event: service supplied the actual output
                        elif item_type == "function_call_output":
                            call_id = getattr(item, "call_id", None) or getattr(item, "id", None)
                            output = getattr(item, "output", "")
                            name = getattr(item, "name", None) or getattr(item, "function_name", None) or getattr(item, "tool_name", None)
                            args = getattr(item, "arguments", None) or getattr(item, "input", None) or getattr(item, "tool_input", None)
                            parsed_args = _normalize_tool_args(args) if args is not None else None
                            if not call_id:
                                continue

                            # Update tool_calls list entries (set name/args if supplied)
                            for tc in tool_calls:
                                if tc.get("call_id") == call_id:
                                    tc["output"] = str(output)
                                    if name:
                                        tc["name"] = name
                                    if parsed_args:
                                        tc["arguments"] = parsed_args

                            # Update processing_items meta and re-render
                            for it in processing_items:
                                if it.get("type") == "tool" and it.get("meta", {}).get("call_id") == call_id:
                                    it["meta"]["output"] = str(output)
                                    if name:
                                        it["meta"]["name"] = name
                                    if parsed_args:
                                        it["meta"]["arguments"] = parsed_args
                            ensure_processing_area()
                            render_processing()

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
                        # Continue instead of breaking so follow-up rounds can run
                        continue

                    case _:
                        pass

    # Build assistant message dict to append to history
    message = {"role": "assistant"}
    if reasoning_content_response:
        message["reasoning_content"] = reasoning_content_response
    if content_response:
        message["content"] = content_response
    if tool_calls:
        message["tool_calls"] = tool_calls

    # Clear temporary streaming bubble; history rendering will draw final message.
    assistant_placeholder.empty()
    return message if reasoning_content_response or content_response or tool_calls else None



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
        tool_calls = msg.get("tool_calls", [])

        with st.chat_message(role):
            # Show reasoning in PROCESSING expander if present
            if reasoning or tool_calls:
                with st.expander("PROCESSING"):
                    if reasoning:
                        st.markdown(reasoning)
                    
                    # Display tool calls in a clean format. Support both
                    # the older {name, arguments} schema and the newer
                    # function_call_output schema.
                    for tool_call in tool_calls:
                        # Render as tool_name(arguments)
                        tool_name = tool_call.get("name", "Không rõ")
                        args = tool_call.get("arguments", {}) or {}
                        args_text = json.dumps(args, ensure_ascii=False) if args else "{}"
                        header = f"**`{tool_name}({args_text})`**" if tool_name else f"**`function_call_output({args_text})`**"
                        st.markdown(header, unsafe_allow_html=True)
                        output = tool_call.get("output", "")
                        if output:
                            try:
                                parsed = json.loads(output)
                                st.json(parsed)
                            except Exception:
                                st.code(output)

            # Show main content
            if not content:
                continue

            if content.startswith("{") and content.endswith("}"):
                try:
                    json_data = json.loads(content)
                    st.json(json_data)
                except Exception:
                    st.markdown(content)
            else:
                st.markdown(content)