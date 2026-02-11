import json
import streamlit as st



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