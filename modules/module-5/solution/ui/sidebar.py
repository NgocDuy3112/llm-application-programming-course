# Module 5
import streamlit as st


def render_sidebar():
    st.sidebar.title("Cài đặt Chatbot")
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        key="temperature"
    )
    st.sidebar.number_input(
        label="Độ dài tối đa của phản hồi (Max Output Tokens)",
        min_value=2048,
        max_value=131072,
        value=65536,
        step=256,
        key="max_output_tokens"
    )
    st.sidebar.text_area(
        label="Câu lệnh hệ thống (System Prompt)",
        height=200,
        placeholder="Bạn là một trợ lý hữu ích và thân thiện.",
        key="system_prompt"
    )
    st.sidebar.radio(
        label="Chọn chế độ quản lý ngữ cảnh",
        options=[
            "Tắt",
            "Cửa sổ trượt (sliding window)",
            "Tóm tắt (summarization)"
        ],
        index=0,
        key="context_management_mode"
    )
    if st.sidebar.button("Cập nhật cài đặt"):
        st.sidebar.success("Đã cập nhật cấu hình!")
        with st.sidebar.expander("Xem chi tiết cấu hình", expanded=True):
            st.markdown(f"**Độ sáng tạo (Temperature):** {st.session_state.temperature}")
            st.markdown(f"**Số lượng token tối đa (Max Output Tokens):** {st.session_state.max_output_tokens}")
            st.markdown(f"**Câu lệnh hệ thống (System Prompt):** {st.session_state.system_prompt}")
            st.markdown(f"**Chế độ quản lý ngữ cảnh (Context Management Mode):** {st.session_state.context_management_mode}")