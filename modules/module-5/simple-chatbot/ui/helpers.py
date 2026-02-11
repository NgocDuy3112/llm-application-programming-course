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



def display_streaming_response(response_generator) -> None:
    response_container = st.empty()
    reasoning_content_response = ""
    content_response = ""
    for event in response_generator:
        match event.type:
            case OpenAIResponseAPIStreamingState.REASONING_IN_PROGRESS:
                reasoning_content_response += event.delta
                with response_container.expander("REASONING"):
                    st.markdown(reasoning_content_response)
            case OpenAIResponseAPIStreamingState.TEXT_STREAMING_IN_PROGRESS:
                content_response += event.delta
                response_container.markdown(content_response)
            case OpenAIResponseAPIStreamingState.RESPONSE_COMPLETED:
                break



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