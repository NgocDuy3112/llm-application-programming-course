import streamlit as st


def render_sidebar():
    st.sidebar.title("Cài đặt Chatbot")
    st.sidebar.slider(
        label="Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.01,
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
    st.sidebar.button(
        "Cập nhật cài đặt",
        key="update_settings"
    )
    if st.session_state.get("update_settings"):
        temperature = st.session_state.get("temperature", 0.5)
        max_output_tokens = st.session_state.get("max_output_tokens", 65536)
        st.sidebar.markdown(f"**Temperature:** {temperature}")
        st.sidebar.markdown(f"**Max Output Tokens:** {max_output_tokens}")