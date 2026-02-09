from streamlit_handlers import *
from chat_service import *



def main():
    st.title("Xây dựng chatbot đơn giản cùng Streamlit")
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { width: 420px; min-width: 420px; }
        .css-1d391kg { width: 420px; }
        main { margin-left: 440px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    sidebar_state = sidebar()
    client = OpenAI(
        api_key=sidebar_state["api_key"], 
        base_url="https://api.groq.com/openai/v1"
    )
    chat_service = SlidingWindowChatService(client=client, history=st.session_state["chat_history"])
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
                    content = response.output_text
                display_response(content)
                
            except Exception as e:
                st.error(f"❌ [ERROR] {str(e)}")



if __name__ == "__main__":
    main()