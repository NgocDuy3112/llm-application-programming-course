"""
Module 5 - Chat Interface

Mô tả: Streamlit chat UI component cho chatbot. Component này xử lý:
- Hiển thị chat history
- Nhận user input
- Gọi engine để lấy response
- Hiển thị phản hồi từ AI

TODO: Hoàn thành hàm render_chat_interface dưới đây:

1. Hiển thị tiêu đề "Xây dựng chatbot cơ bản" bằng st.title()
2. Khởi tạo chat_history trong session_state nếu chưa có
3. Hiển thị lịch sử chat bằng cách duyệt qua st.session_state.chat_history
4. Tạo chat input box bằng st.chat_input()
5. Khi user gửi tin nhắn:
   a. Hiển thị tin nhắn user bằng st.chat_message("user")
   b. Lưu tin nhắn user vào chat_history
   c. Gọi engine.response() với các tham số từ session_state
   d. Hiển thị phản hồi bằng st.chat_message("assistant")
   e. Lưu phản hồi vào chat_history
   f. Gọi st.rerun() để cập nhật UI

Gợi ý: Sử dụng st.spinner() để hiển thị loading khi chờ phản hồi.
"""

import streamlit as st


def render_chat_interface(engine):
    """
    Render giao diện chat chính.

    Args:
        engine (object): Object implementing `.response(model, user_prompt, ...)` method
    """
    # TODO 1: Hiển thị tiêu đề "Xây dựng chatbot cơ bản" bằng st.title()
    
    # TODO 2: Khởi tạo chat_history trong session_state nếu chưa có
    # st.session_state.chat_history = []
    
    # TODO 3: Hiển thị lịch sử chat
    # Duyệt qua st.session_state.chat_history
    # Mỗi entry có "role" và "content"
    # Sử dụng st.chat_message(entry["role"]).markdown(entry["content"])
    
    # TODO 4: Tạo chat input box bằng st.chat_input()
    # Placeholder: "Nhập tin nhắn của bạn ở đây..."
    
    # TODO 5: Xử lý khi user gửi tin nhắn
    # if user_input:
    #   a. Hiển thị tin nhắn user bằng st.chat_message("user").markdown(user_input)
    #   b. Lưu vào chat_history: {"role": "user", "content": user_input}
    #   c. Gọi engine.response() với:
    #      - model=st.session_state.selected_model
    #      - user_prompt=user_input
    #      - temperature=st.session_state.temperature
    #      - max_tokens=st.session_state.max_tokens
    #      - system_prompt=st.session_state.get("system_prompt", "")
    #   d. Hiển thị phản hồi bằng st.chat_message("assistant").markdown(assistant_reply)
    #   e. Lưu vào chat_history: {"role": "assistant", "content": assistant_reply}
    #   f. Gọi st.rerun() để cập nhật UI
    pass