import json
import streamlit as st
from settings import Settings

from service.chat import *
from ui.helpers import *



settings = Settings()




def sidebar():
    with st.sidebar:
        api_key = st.text_input(
            "Nhập API key",
            value=settings.GROQ_API_KEY,
            type="password"
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
        )
        max_output_tokens = st.slider(
            "Số tokens tối đa",
            min_value=1,
            max_value=65000,
            value=65000,
            step=1
        )
        custom_instructions = st.text_area(
            "Chỉ dẫn tùy chỉnh",
            value="",
            height=200,
        )
        streaming_mode = st.toggle(
            "Chế độ streaming",
            value=st.session_state.get("streaming_mode_widget", False),
            key="streaming_mode_widget"
        )
        with st.expander("Quản lý ngữ cảnh"):
            def _on_sliding_change():
                # If enabling sliding window, disable summarization
                if st.session_state.get("sliding_window_mode_widget", False):
                    st.session_state["summarization_mode_widget"] = False

            def _on_summarization_change():
                # If enabling summarization, disable sliding window
                if st.session_state.get("summarization_mode_widget", False):
                    st.session_state["sliding_window_mode_widget"] = False

            sliding_window_mode = st.checkbox(
                "Cửa số trượt",
                value=st.session_state.get("sliding_window_mode_widget", True),
                key="sliding_window_mode_widget",
                on_change=_on_sliding_change,
            )
            summarization_mode = st.checkbox(
                "Tóm tắt",
                value=st.session_state.get("summarization_mode_widget", False),
                key="summarization_mode_widget",
                on_change=_on_summarization_change,
            )
        
    state = {
        "api_key": api_key,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "custom_instructions": custom_instructions,
        "streaming_mode": streaming_mode,
        "sliding_window_mode": sliding_window_mode,
        "summarization_mode": summarization_mode,
    }
    return state
