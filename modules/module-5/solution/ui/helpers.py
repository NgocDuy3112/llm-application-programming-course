import json
import streamlit as st
from streaming_types import OpenAIResponseAPIStreamingState



def display_response(response) -> dict | None:
    """Parse a non-streaming response and return assistant message dict."""
    reasoning_content = ""
    content = ""

    for block in getattr(response, "output", []) or []:
        # defensive access: block.content may be None or empty
        content_items = getattr(block, "content", []) or []
        block_content = getattr(content_items[0], "text", "") if content_items else ""
        block_type = getattr(block, "type", None)

        if block_type == "reasoning":
            summary = getattr(block, "summary", None) or block_content
            if summary:
                reasoning_content = summary
        elif block_type == "message":
            if block_content:
                content = block_content
        else:
            # unknown block types are ignored
            continue

    message = {"role": "assistant"}
    if reasoning_content:
        message["reasoning_content"] = reasoning_content
    if content:
        message["content"] = content

    return message if reasoning_content or content else None



def display_streaming_response(response_generator, stream_slot=None) -> dict | None:
    """Render streaming assistant output and return final message dict.

    Args:
        response_generator: streaming response iterator
        stream_slot: optional placeholder created by st.empty()
    """
    assistant_placeholder = stream_slot or st.empty()
    reasoning_content_response = ""
    content_response = ""

    with assistant_placeholder.container():
        with st.chat_message("assistant"):
            reasoning_placeholder = st.empty()
            content_placeholder = st.empty()
            reasoning_expander = None

            for event in response_generator:
                etype = getattr(event, "type", None)
                match etype:
                    case OpenAIResponseAPIStreamingState.RESPONSE_REASONING_SUMMARY_TEXT_DELTA:
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

                    case _:
                        pass

    message = {"role": "assistant"}
    if reasoning_content_response:
        message["reasoning_content"] = reasoning_content_response
    if content_response:
        message["content"] = content_response

    # Clear temporary streaming bubble; history rendering will draw final message.
    assistant_placeholder.empty()
    return message if reasoning_content_response or content_response else None



def render_chat_history(chat_history: list[dict[str, str]], container=None) -> None:
    """
    Render chat history in Streamlit
    
    Args:
        chat_history: List of chat messages
    """
    container = container or st.container()

    with container:
        for msg in chat_history:
            role = msg.get("role", "user")
            reasoning = msg.get("reasoning_content", "")
            content = msg.get("content", "")

            with st.chat_message(role):
                if reasoning:
                    with st.expander("PROCESSING"):
                        st.markdown(reasoning)

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