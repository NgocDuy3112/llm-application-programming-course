import streamlit as st


def render_chat_interface(engine):
    """
    Render giao diện chat chính.

    Args:
        engine (object): Object implementing `.response(model, user_prompt, ...)` method
    """
    # TODO 2a: Hiển thị tiêu đề "Xây dựng chatbot cơ bản" bằng st.title()
    
    # TODO 2b: Khởi tạo chat_history trong session_state nếu chưa có
    # st.session_state.chat_history = []
    
    # TODO 2c: Hiển thị lịch sử chat
    # Duyệt qua st.session_state.chat_history
    # Mỗi entry có "role" và "content"
    # Sử dụng st.chat_message(entry["role"]).markdown(entry["content"])
    
    # TODO 2d: Tạo chat input box bằng st.chat_input()
    # Placeholder: "Nhập tin nhắn của bạn ở đây..."
    
    # TODO 2e: Xử lý khi user gửi tin nhắn
    # if user_input:
    #   a. Hiển thị tin nhắn user bằng st.chat_message("user").markdown(user_input)
    #   b. Lưu vào chat_history: {"role": "user", "content": user_input}
    #   c. Gọi engine.response() với:
    #      - model=st.session_state.selected_model
    #      - user_prompt=user_input
    #   d. Hiển thị phản hồi bằng st.chat_message("assistant").markdown(assistant_reply)
    #   e. Lưu vào chat_history: {"role": "assistant", "content": assistant_reply}
    #   f. Gọi st.rerun() để cập nhật UI
    pass