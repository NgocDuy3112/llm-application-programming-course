import streamlit as st


def sidebar():
    """
    Render control panel in sidebar và trả về cấu hình người dùng chọn.
    Gợi ý: Dùng st.slider (temperature), st.number_input (max_tokens), st.text_area (system), st.toggle (streaming). 
    Sử dụng 'key' trong các component để st.session_state tự lưu.
    """
    with st.sidebar:
        # TODO 1.3: Thêm st.slider cho 'temperature' (0.0 - 1.0)
        # TODO 1.4: Thêm st.number_input cho 'max_output_tokens' (1 - 32768)
        # TODO 1.5: Thêm st.text_area cho 'custom_instructions' (Nằm lòng bạn là ai?)
        # TODO 1.6: Thêm st.toggle cho 'streaming_mode_widget' (Bật hiệu ứng gõ chữ)
        # TODO 5.1/4.1: Thêm st.radio chọn chế độ ngữ cảnh ('off', 'sliding_window', 'summarization')
        pass
