import json
import streamlit as st
from enum import Enum


class OpenAIResponseAPIStreamingState(str, Enum):
    TEXT_STREAMING_IN_PROGRESS = "response.output_text.delta"
    TEXT_STREAMING_DONE = "response.output_text.done"
    REASONING_IN_PROGRESS = "response.reasoning_text.delta"
    REASONING_DONE = "response.reasoning_text.done"
    RESPONSE_COMPLETED = "response.completed"
    RESPONSE_INCOMPLETED = "response.incomplete"



def display_response(response) -> None:
    for block in response.output:
        content = block.content[0].text
        match block.type:
            case 'reasoning':
                if (summary := block.summary or content):
                    with st.expander("REASONING"):
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
    content_placeholder = st.empty()
    reasoning_placeholder = st.empty()
    reasoning_expander = None
    reasoning_content_response = ""
    content_response = ""

    for event in response_generator:
        # event.type can be one of our enum values
        etype = getattr(event, "type", None)

        if etype == OpenAIResponseAPIStreamingState.REASONING_IN_PROGRESS:
            delta = getattr(event, "delta", "")
            if delta:
                reasoning_content_response += delta
                if reasoning_expander is None:
                    reasoning_expander = reasoning_placeholder.expander("REASONING")
                reasoning_expander.markdown(reasoning_content_response)

        elif etype == OpenAIResponseAPIStreamingState.TEXT_STREAMING_IN_PROGRESS:
            delta = getattr(event, "delta", "")
            if delta:
                content_response += delta
                content_placeholder.markdown(content_response)

        elif etype == OpenAIResponseAPIStreamingState.RESPONSE_COMPLETED:
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
                with st.expander("REASONING"):
                    st.markdown(reasoning)
            if content.startswith("{") and content.endswith("}"):
                json_data = json.loads(content)
                st.json(json_data)
            else:
                st.markdown(content)