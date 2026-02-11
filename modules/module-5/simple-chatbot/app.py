from ui.sidebar import *
from service.chat import *
from rich import print


def main():
    st.title("Xây dựng chatbot đơn giản")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    sidebar_state = sidebar()
    client = OpenAI(
        api_key=sidebar_state["api_key"], 
        base_url="https://api.groq.com/openai/v1"
    )
    if sidebar_state["summarization_mode"]:
        chat_service = SummarizationChatService(client=client, history=st.session_state["chat_history"])
    elif sidebar_state["sliding_window_mode"]:
        chat_service = SlidingWindowChatService(client=client, history=st.session_state["chat_history"])
    else:
        chat_service = ChatService(client=client)
    render_chat_history(st.session_state["chat_history"])
    user_input = st.chat_input("Nhập tin nhắn của bạn...")
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                response = chat_service.response(
                    input=user_input,
                    model="openai/gpt-oss-20b",
                    instructions=sidebar_state["custom_instructions"],
                    max_output_tokens=sidebar_state["max_output_tokens"],
                    temperature=sidebar_state["temperature"]
                )
                with st.spinner("Đang phản hồi..."):
                    display_response(response)
            except Exception as e:
                st.error(f"❌ [ERROR] {str(e)}")



if __name__ == "__main__":
    main()