"""
Module 5 - Sidebar

Mô tả: Streamlit sidebar component cho chatbot. Component này xử lý:
- Chọn nhà cung cấp mô hình (Provider: Groq hoặc Ollama)
- Chọn mô hình cụ thể dựa trên provider
- Cấu hình temperature, max tokens, system prompt
- Chọn chế độ quản lý ngữ cảnh (Tắt hoặc Sliding Window)
- Cấu hình sliding window turns (nếu bật)
- Toggle sử dụng công cụ
- Nút cập nhật cài đặt

TODO: Hoàn thành hàm render_sidebar dưới đây:

1. Khởi tạo các giá trị mặc định trong session_state:
   - selected_provider: Provider.GROQ.value
   - selected_model: MODELS_BY_PROVIDER[Provider.GROQ.value][0]
   - temperature: 0.25
   - max_completion_tokens: 5120
   - system_prompt: ""
   - context_management_mode: ContextManagementMode.OFF.value
   - sliding_window_turns: 5
   - enable_tools: False

2. Tạo sidebar title "Cài đặt Chatbot"

3. Tạo selectbox chọn Provider (GROQ, OLLAMA)

4. Tạo selectbox chọn Model (dựa trên Provider đã chọn)
   - Sử dụng MODELS_BY_PROVIDER dictionary

5. Tạo slider cho Temperature (0.0 - 1.0, step 0.05)

6. Tạo number_input cho Max Completion Tokens (2048 - 131072, step 256)

7. Tạo text_area cho System Prompt

8. Tạo radio cho Context Management Mode (OFF, SLIDING_WINDOW)

9. Nếu chọn SLIDING_WINDOW, tạo number_input cho số tin nhắn trong cửa sổ trượt

10. Tạo toggle cho "Sử dụng công cụ"

11. Tạo button "Cập nhật cài đặt" để reset chat_history
"""

import streamlit as st
from custom_types import Provider, ContextManagementMode
from custom_types import MODELS_BY_PROVIDER


def render_sidebar():
    """
    Render sidebar với các controls cấu hình chung của chatbot.
    
    Side effects: cập nhật các keys trong `st.session_state` và reset
    `st.session_state.chat_history` khi nhấn nút "Cập nhật cài đặt".
    """
    
    # TODO 1: Khởi tạo các giá trị mặc định trong session_state
    # if "selected_provider" not in st.session_state:
    #     st.session_state.selected_provider = Provider.GROQ.value
    # if "selected_model" not in st.session_state:
    #     st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]
    # (tương tự cho temperature, max_completion_tokens, system_prompt, 
    #  context_management_mode, sliding_window_turns, enable_tools)
    
    # TODO 2: Tạo sidebar title "Cài đặt Chatbot"
    
    # TODO 3: Tạo selectbox chọn Provider
    # st.sidebar.selectbox(
    #     label="Chọn nhà cung cấp mô hình",
    #     options=[Provider.GROQ.value, Provider.OLLAMA.value],
    #     index=0,
    #     key="selected_provider"
    # )
    
    # TODO 4: Tạo selectbox chọn Model dựa trên Provider
    # available_models = MODELS_BY_PROVIDER.get(st.session_state.selected_provider, [])
    # st.sidebar.selectbox(
    #     label="Chọn mô hình",
    #     options=available_models,
    #     index=0,
    #     key="selected_model"
    # )
    
    # TODO 5: Tạo slider cho Temperature (0.0 - 1.0, value=0.25, step=0.05)
    
    # TODO 6: Tạo number_input cho Max Completion Tokens (min=2048, max=131072, value=5120, step=256)
    
    # TODO 7: Tạo text_area cho System Prompt (height=200)
    
    # TODO 8: Tạo radio cho Context Management Mode
    # options=[ContextManagementMode.OFF.value, ContextManagementMode.SLIDING_WINDOW.value]
    
    # TODO 9: Nếu chọn SLIDING_WINDOW, tạo number_input cho số tin nhắn (min=1, max=50, value=5, step=1)
    
    # TODO 10: Tạo toggle cho "Sử dụng công cụ" (value=False)
    
    # TODO 11: Tạo button "Cập nhật cài đặt"
    # Khi nhấn: reset chat_history và xóa chatbot_engine trong session_state
    pass