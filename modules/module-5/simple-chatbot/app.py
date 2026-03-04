import os
from rich import print
from dotenv import load_dotenv

from ui.sidebar import *
from service.chat import *


load_dotenv(dotenv_path="../.env", override=True)



def main():
    st.title("Xây dựng chatbot đơn giản")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    sidebar()
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    if st.session_state.get("summarization_mode_widget", False):
        chat_service = SummarizationChatService(client=client, history=st.session_state["chat_history"])
    elif st.session_state.get("sliding_window_mode_widget", False):
        chat_service = SlidingWindowChatService(client=client, history=st.session_state["chat_history"])
    else:
        chat_service = ChatService(client=client)
    render_chat_history(st.session_state["chat_history"])
    user_input = st.chat_input(
        placeholder="Nhập tin nhắn của bạn...",
        key="user_input",
        disabled=False
    )
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                response = chat_service.response(
                    input=user_input,
                    model="openai/gpt-oss-20b",
                    instructions=st.session_state.get("custom_instructions", ""),
                    max_output_tokens=st.session_state.get("max_output_tokens", 2048),
                    stream=st.session_state.get("streaming_mode_widget", False),
                    temperature=st.session_state.get("temperature", 0.25)
                )
                if not st.session_state.get("streaming_mode_widget", False):
                    with st.spinner("Đang phản hồi..."):
                        display_response(response)
                else:
                    assistant_msg = display_streaming_response(response)
                    if assistant_msg:
                        st.session_state["chat_history"].append(assistant_msg)
            except Exception as e:
                st.error(f"❌ [ERROR] {str(e)}")



if __name__ == "__main__":
    main()