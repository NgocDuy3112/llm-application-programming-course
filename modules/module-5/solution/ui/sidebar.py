import streamlit as st

from service.chat import *
from ui.helpers import *




def sidebar():
    with st.sidebar:
        st.slider(
            "Độ sáng tạo (temperature)",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
            key="temperature"
        )
        st.number_input(
            "Độ dài phản hồi tối đa (tokens)",
            min_value=256,
            max_value=131072,
            value=2048,
            step=32,
            key="max_output_tokens"
        )
        st.text_area(
            label="Chỉ dẫn tùy chỉnh",
            placeholder="Trả lời bằng tiếng Việt...",
            height=200,
            key="custom_instructions"
        )
        st.toggle(
            label="Chế độ streaming",
            value=st.session_state.get("streaming_mode_widget", False),
            disabled=False,
            key="streaming_mode_widget"
        )
        if st.session_state.get("sliding_window_mode_widget", False):
            initial_index = 1
        elif st.session_state.get("summarization_mode_widget", False):
            initial_index = 2
        else:
            initial_index = 0

        def _on_context_mode_change():
            val = st.session_state.get("context_mode_widget", "off")
            st.session_state["sliding_window_mode_widget"] = (val == "sliding_window")
            st.session_state["summarization_mode_widget"] = (val == "summarization")

        st.radio(
            "Chế độ quản lý ngữ cảnh",
            options=["off", "sliding_window", "summarization"],
            format_func=lambda x: {
                "sliding_window": "Cửa sổ trượt",
                "summarization": "Tóm tắt",
                "off": "Tắt"
            }[x],
            index=initial_index,
            key="context_mode_widget",
            on_change=_on_context_mode_change,
        )

