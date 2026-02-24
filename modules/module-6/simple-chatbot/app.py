from settings import Settings
from tavily import TavilyClient

from ui.sidebar import *
from service.chat import *
from logger import ChatbotLogger


settings = Settings()
tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
logger = ChatbotLogger.get_logger("streamlit_app")


def main():
    st.title("Xây dựng chatbot đơn giản")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
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
    user_input = st.chat_input("Nhập tin nhắn của bạn...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                response = chat_service.response(
                    input=user_input,
                    model=sidebar_state["model"],
                    instructions=sidebar_state["custom_instructions"],
                    max_output_tokens=sidebar_state["max_output_tokens"],
                    temperature=sidebar_state["temperature"],
                    stream=sidebar_state["streaming_mode"]
                )
                if not sidebar_state["streaming_mode"]:
                    with st.spinner("Đang phản hồi..."):
                        display_response(response)
                else:
                    assistant_msg = display_streaming_response(response)
                    if assistant_msg:
                        st.session_state["chat_history"].append(assistant_msg)
            except Exception as e:
                logger.exception(
                    "Error processing user input; provider=%s, model=%s, error=%s",
                    chat_service.provider.value,
                    sidebar_state.get("model"),
                    e,
                )
                st.error(f"❌ [ERROR] {str(e)}")



if __name__ == "__main__":
    main()