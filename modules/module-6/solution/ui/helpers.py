import json
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

    with assistant_placeholder.container():
        with st.chat_message("assistant"):
            reasoning_placeholder = st.empty()
            content_placeholder = st.empty()
            reasoning_expander = None

            for event in response_generator:
                etype = getattr(event, "type", None)
                
                match etype:
                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DELTA:
                        delta = getattr(event, "delta", "")
                        if delta:
                            reasoning_content_response += delta
                            if reasoning_expander is None:
                                reasoning_expander = reasoning_placeholder.expander("PROCESSING")
                            reasoning_expander.markdown(reasoning_content_response)

                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DELTA:
                        delta = getattr(event, "delta", "")
                        if delta:
                            reasoning_content_response += delta
                            if reasoning_expander is None:
                                reasoning_expander = reasoning_placeholder.expander("PROCESSING")
                            reasoning_expander.markdown(reasoning_content_response)

                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DONE:
                        done_text = getattr(event, "text", "")
                        if done_text:
                            reasoning_content_response = done_text
                            if reasoning_expander is None:
                                reasoning_expander = reasoning_placeholder.expander("PROCESSING")
                            reasoning_expander.markdown(reasoning_content_response)

                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DONE:
                        done_text = getattr(event, "text", "")
                        if done_text:
                            reasoning_content_response = done_text
                            if reasoning_expander is None:
                                reasoning_expander = reasoning_placeholder.expander("PROCESSING")
                            reasoning_expander.markdown(reasoning_content_response)

                    case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_ITEM_DONE:
                        item = getattr(event, "item", None) or getattr(event, "output_item", None)
                        if not item:
                            continue

                        item_type = getattr(item, "type", None)
                        if item_type in ("function_call", "tool_call"):
                            parsed_args = _normalize_tool_args(getattr(item, "arguments", None))
                            tool_name = getattr(item, "name", "")
                            tool_calls.append({
                                "name": tool_name,
                                "arguments": parsed_args,
                            })
                            
                            # Display tool call in reasoning expander
                            if reasoning_expander is None:
                                reasoning_expander = reasoning_placeholder.expander("PROCESSING")
                            
                            # Add tool call to reasoning content
                            tool_args_text = json.dumps(parsed_args, ensure_ascii=False) if parsed_args else "{}"
                            reasoning_expander.markdown(f"**`{tool_name}({tool_args_text})`**", unsafe_allow_html=True)

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
                        break

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
                    
                    # Display tool calls in a clean format
                    for tool_call in tool_calls:
                        tool_name = tool_call.get("name", "Không rõ")
                        args = tool_call.get("arguments", {})
                        args_text = json.dumps(args, ensure_ascii=False) if args else "{}"
                        st.markdown(f"**`{tool_name}({args_text})`**", unsafe_allow_html=True)

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