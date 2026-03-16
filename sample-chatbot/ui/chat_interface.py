import streamlit as st

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice



def render_chat_interface(engine: object):
    global_logger.debug("Rendering chat interface")
    st.title("Xây dựng chatbot cơ bản")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.container():
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).markdown(entry["content"])
        global_logger.debug(f"Displayed {len(st.session_state.chat_history)} messages from chat history")

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        global_logger.debug(f"Processing user input: {user_input[:50]}...")
        with st.chat_message("user"):
            st.markdown(user_input)
        # Only append to UI chat_history, engine.memory handles its own buffer
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        assistant_reply = engine.response(
            model=st.session_state.selected_model,
            input=user_input,
            temperature=st.session_state.temperature,
            tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
            tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            max_output_tokens=st.session_state.max_output_tokens,
            instruction=st.session_state.instruction
        )
        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply)}")
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        # Only append to UI chat_history, engine.memory handles its own buffer
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        global_logger.debug(f"Updated chat history, total messages: {len(st.session_state.chat_history)}")