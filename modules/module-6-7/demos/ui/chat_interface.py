import streamlit as st
from logger import global_logger



def render_chat_interface(engine: object):
    global_logger.debug("Rendering chat interface")
    st.title("Xây dựng chatbot cơ bản")

    with st.container():
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).write(entry["message"])

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        global_logger.debug(f"Processing user input: {user_input[:50]}...")
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        assistant_reply = engine.response(
            model=st.session_state.selected_model,
            input=user_input,
            temperature=st.session_state.temperature,
            max_output_tokens=st.session_state.max_output_tokens,
            instruction=st.session_state.instruction
        )
        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply)}")
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        st.session_state.chat_history.append({"role": "assistant", "message": assistant_reply})