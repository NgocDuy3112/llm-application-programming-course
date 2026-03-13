# Module 5
import streamlit as st



def render_chat_interface(engine: object):
    st.header("Xây dựng chatbot cơ bản")
    for entry in st.session_state.chat_history:
        st.chat_message(entry["role"]).write(entry["message"])
    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    assistant_reply = engine.response(
                        model="openai/gpt-oss-20b", 
                        input=user_input,
                        temperature=st.session_state.temperature,
                        max_output_tokens=st.session_state.max_output_tokens,
                    )
                    st.markdown(assistant_reply)
                    st.session_state.chat_history.append({"role": "assistant", "message": assistant_reply})
                except Exception as e:
                    st.error(f"Lỗi rồi: {e}")