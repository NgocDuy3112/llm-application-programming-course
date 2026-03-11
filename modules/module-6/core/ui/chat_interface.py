import streamlit as st



def render_chat_interface(engine: object):
    st.title("Xây dựng chatbot cơ bản")

    with st.container():
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).write(entry["message"])

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        assistant_reply = engine.response(
            model=st.session_state.selected_model,
            input=user_input,
            temperature=st.session_state.temperature,
            max_output_tokens=st.session_state.max_output_tokens,
            instruction=st.session_state.instruction
        )
        with st.chat_message("assistant"):
            st.write(assistant_reply)
        st.session_state.chat_history.append({"role": "assistant", "message": assistant_reply})