import json
import streamlit as st
from streaming_types import OpenAIResponseAPIStreamingState



def display_response(response) -> None:
    for block in response.output:
        content = block.content[0].text
        match block.type:
            case 'reasoning':
                if (summary := block.summary or content):
                    with st.expander(label="PROCESSING", expanded=True):
                        st.markdown(summary)
            case 'message':
                if content.startswith("{") and content.endswith("}"):
                    json_data = json.loads(content)
                    st.json(json_data)
                else:
                    st.markdown(content)
            case _:
                st.error(f"❌ [ERROR] Unsupported block type: {block.type}")



def display_streaming_response(response_generator) -> dict | None:
    """Consume a streaming response and render it incrementally.

    Returns a dict suitable for appending to `chat_history` when the stream completes.
    """
    # Separate placeholders so reasoning and content don't overwrite each other
    reasoning_placeholder = st.empty()
    content_placeholder = st.empty()
    reasoning_expander = None
    reasoning_content_response = ""
    content_response = ""

    for event in response_generator:
        # event.type can be one of our enum values
        etype = getattr(event, "type", None)
        match etype:
            case OpenAIResponseAPIStreamingState.RESPONSE_CREATED:
                print("[DEBUG] Stream created")
            case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_TEXT_DELTA:
                delta = getattr(event, "delta", "")
                if delta:
                    reasoning_content_response += delta
                    if reasoning_expander is None:
                        reasoning_expander = reasoning_placeholder.expander("PROCESSING")
                reasoning_expander.markdown(reasoning_content_response)

            case OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DELTA:
                delta = getattr(event, "delta", "")
                if delta:
                    content_response += delta
                    content_placeholder.markdown(content_response)

            case OpenAIResponseAPIStreamingState.RESPONSE_COMPLETED:
                break

    # Build assistant message dict to append to history
    message = {"role": "assistant"}
    if reasoning_content_response:
        message["reasoning_content"] = reasoning_content_response
    if content_response:
        message["content"] = content_response

    return message



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
        
        with st.chat_message(role):
            if reasoning:
                with st.expander("PROCESSING"):
                    st.markdown(reasoning)
            if content.startswith("{") and content.endswith("}"):
                json_data = json.loads(content)
                st.json(json_data)
            else:
                st.markdown(content)