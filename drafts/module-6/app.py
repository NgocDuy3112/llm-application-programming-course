import streamlit as st

from core.settings import Settings
from tavily import TavilyClient

from core.ui.sidebar import sidebar
from core.orchestrator.chat_service import ChatService
from core.orchestrator.tools import DEFAULT_TOOLS
from core.logger import ChatbotLogger
from core.ui.helpers import render_chat_history, display_streaming_response


settings = Settings()
tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
logger = ChatbotLogger.get_logger("streamlit_app")



def main():
    st.title("Xây dựng chatbot tích hợp chức năng tìm kiếm với API-based LLM")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False
    sidebar_state = sidebar()
    api_key = settings.get_api_key(sidebar_state["model_provider"].api_key)
    if sidebar_state["model_provider"].api_key and not api_key:
        st.warning(
            f"Chưa tìm thấy API key trong .env ({sidebar_state['model_provider'].api_key})."
        )
    chat_service = ChatService(
        provider=sidebar_state["model_provider"], 
        api_key=api_key, 
        history=st.session_state["chat_history"]
    )
    render_chat_history(st.session_state["chat_history"])
    user_input = st.chat_input(
        "Nhập tin nhắn của bạn...",
        disabled=st.session_state["is_generating"]
    )

    if user_input and not st.session_state["is_generating"]:
        st.session_state["pending_input"] = user_input
        st.session_state["is_generating"] = True
        # Collapse existing REASONING expanders when the user submits a new message.
        st.session_state["collapse_processing"] = True
        st.rerun()

    if st.session_state.get("is_generating") and st.session_state.get("pending_input"):
        user_input = st.session_state.pop("pending_input")
        with st.chat_message("user"):
            st.markdown(user_input)
        try:
            response = chat_service.response(
                input=user_input,
                model=sidebar_state["model"],
                instructions=sidebar_state["custom_instructions"],
                max_output_tokens=sidebar_state["max_output_tokens"],
                temperature=sidebar_state["temperature"],
                tools=DEFAULT_TOOLS if sidebar_state.get("enable_web_search", True) else [],
            )
            assistant_msg = display_streaming_response(response)
            if assistant_msg:
                st.session_state["chat_history"].append(assistant_msg)
                # New assistant message should show its reasoning expander;
                # clear the collapse flag so this message's expander remains open.
                st.session_state["collapse_processing"] = False
        except Exception as e:
            logger.exception("Streaming error: %s", e)
            with st.chat_message("assistant"):
                st.error(f"❌ [ERROR] {str(e)}")
        st.session_state["is_generating"] = False
        st.rerun()



if __name__ == "__main__":
    main()