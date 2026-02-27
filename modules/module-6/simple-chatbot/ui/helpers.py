import json
import streamlit as st

from streaming_types import OpenAIResponseAPIStreamingState
from logger import ChatbotLogger



logger = ChatbotLogger.get_logger("streamlit_handlers")


def _sanitize_reasoning_text(text: str, max_chars: int = 1200) -> str:
    """Trim noisy reasoning payloads to keep UI concise and stable."""
    clean = (text or "").strip()
    if not clean:
        return ""
    if len(clean) <= max_chars:
        return clean
    return f"{clean[:max_chars].rstrip()}…"


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


def _render_processing_actions(container, processing_actions: list[dict[str, object]], expanded: bool) -> None:
    """Render reasoning/tool calls as a single ordered timeline."""
    with container.expander("PROCESSING", expanded=expanded):
        for action in processing_actions:
            action_type = action.get("type")
            if action_type == "reasoning":
                content = str(action.get("content", "")).strip()
                if content:
                    st.markdown(content)
            elif action_type == "tool_call":
                tool_name = str(action.get("name", "Không rõ") or "Không rõ")
                args = action.get("arguments", {})
                args_text = json.dumps(args, ensure_ascii=False) if args else "{}"
                st.markdown(f"**`{tool_name}({args_text})`**", unsafe_allow_html=True)



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
    # Placeholder order controls visual order in Streamlit: processing above text.
    reasoning_tool_placeholder = st.empty()
    content_placeholder = st.empty()
    reasoning_stream_text = ""
    reasoning_final_text = ""
    content_response = ""
    processing_actions: list[dict[str, object]] = []
    tool_call_trace: list[dict[str, object]] = []
    current_reasoning_action_idx: int | None = None
    output_text_started = False

    def _upsert_reasoning_action(reasoning_text: str) -> None:
        nonlocal current_reasoning_action_idx
        clean_text = _sanitize_reasoning_text(reasoning_text)
        if not clean_text:
            return

        if current_reasoning_action_idx is None:
            processing_actions.append({"type": "reasoning", "content": clean_text})
            current_reasoning_action_idx = len(processing_actions) - 1
        else:
            processing_actions[current_reasoning_action_idx] = {
                "type": "reasoning",
                "content": clean_text,
            }

        _render_processing_actions(
            container=reasoning_tool_placeholder,
            processing_actions=processing_actions,
            expanded=not output_text_started,
        )

    for event in response_generator:
        # event.type can be one of our enum values
        etype = getattr(event, "type", None)

        match etype:
            case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DELTA:
                delta = getattr(event, "delta", "")
                if delta:
                    reasoning_stream_text += delta
                    _upsert_reasoning_action(reasoning_stream_text)

            case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DONE:
                # Prefer final reasoning payload when available.
                done_text = getattr(event, "text", "")
                if done_text:
                    reasoning_final_text = done_text
                    _upsert_reasoning_action(reasoning_final_text)

            case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DELTA:
                # show raw reasoning only if summary hasn't started
                if not reasoning_final_text:
                    delta = getattr(event, "delta", "")
                    if delta:
                        reasoning_stream_text += delta
                        _upsert_reasoning_action(_sanitize_reasoning_text(reasoning_stream_text))

            case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DONE:
                if not reasoning_stream_text and not reasoning_final_text:
                    done_text = getattr(event, "text", "")
                    if done_text:
                        reasoning_final_text = done_text
                        _upsert_reasoning_action(_sanitize_reasoning_text(reasoning_final_text))

            case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_ITEM_DONE:
                # Capture tool call details from output items when present.
                item = getattr(event, "item", None) or getattr(event, "output_item", None)
                if not item:
                    continue

                item_type = getattr(item, "type", None)
                if item_type in ("function_call", "tool_call"):
                    parsed_args = _normalize_tool_args(getattr(item, "arguments", None))
                    tool_name = getattr(item, "name", "")
                    tool_call_trace.append({
                        "name": tool_name,
                        "arguments": parsed_args,
                    })
                    processing_actions.append({
                        "type": "tool_call",
                        "name": tool_name,
                        "arguments": parsed_args,
                    })
                    # start a new reasoning action after each tool call
                    current_reasoning_action_idx = None
                    # reset any accumulated reasoning text so the next reasoning
                    # event begins with fresh content rather than repeating prior
                    # text.  Without this the new reasoning action would contain
                    # the entire stream from before the tool call.
                    reasoning_stream_text = ""
                    reasoning_final_text = ""

                if processing_actions:
                    _render_processing_actions(
                        container=reasoning_tool_placeholder,
                        processing_actions=processing_actions,
                        expanded=not output_text_started,
                    )

            case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DELTA:
                delta = getattr(event, "delta", "")
                if delta:
                    if not output_text_started:
                        output_text_started = True
                        # Collapse PROCESSING exactly when output text starts streaming.
                        if processing_actions:
                            _render_processing_actions(
                                container=reasoning_tool_placeholder,
                                processing_actions=processing_actions,
                                expanded=False,
                            )
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

    final_reasoning = _sanitize_reasoning_text(reasoning_final_text or reasoning_stream_text)
    if processing_actions:
        _render_processing_actions(
            container=reasoning_tool_placeholder,
            processing_actions=processing_actions,
            expanded=not output_text_started,
        )

    # Build assistant message dict to append to history
    message = {"role": "assistant"}
    if processing_actions:
        message["processing_actions"] = processing_actions
    if final_reasoning:
        message["reasoning_content"] = final_reasoning
    if content_response:
        message["content"] = content_response
    if tool_call_trace:
        message["tool_trace"] = tool_call_trace

    # Only collapse by default when output_text has started streaming.
    message["expand_processing"] = bool(processing_actions) and not output_text_started

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
        processing_actions = msg.get("processing_actions", [])

        # Backward compatibility: older messages only have reasoning/tool_trace.
        if not processing_actions and (reasoning or tool_trace):
            if reasoning:
                processing_actions.append({"type": "reasoning", "content": reasoning})
            for call in tool_trace:
                processing_actions.append({
                    "type": "tool_call",
                    "name": call.get("name", ""),
                    "arguments": call.get("arguments", {}),
                })

        with st.chat_message(role):
            if processing_actions:
                # Determine whether the expander should be open. The app sets
                # `collapse_processing` in session state when the user submits a
                # new message to collapse previous processing boxes.
                collapse_all = st.session_state.get("collapse_processing", False)
                expanded = msg.get("expand_processing", False) and not collapse_all
                _render_processing_actions(
                    container=st,
                    processing_actions=processing_actions,
                    expanded=expanded,
                )
            if content.startswith("{") and content.endswith("}"):
                json_data = json.loads(content)
                st.json(json_data)
            else:
                st.markdown(content)