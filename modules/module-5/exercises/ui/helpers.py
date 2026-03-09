import streamlit as st
import json
from streaming_types import OpenAIResponseAPIStreamingState



def initialize_chat_history():
    """
    Khởi tạo lịch sử chat trong st.session_state và cờ hiệu đang tạo phản hồi
    Gợi ý: 'chat_history' và 'is_generating'.
    """
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False



def render_chat_history(messages: list):
    """
    Render danh sách messages, hỗ trợ text và reasoning (expander 'PROCESSING').
    Gợi ý: Lặp qua 'messages', dùng st.chat_message(role) và st.expander nếu có 'reasoning_content'.
    """
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        reasoning = msg.get("reasoning_content", "")
        with st.chat_message(role):
            if reasoning:
                with st.expander("PROCESSING"):
                    st.markdown(reasoning)
            if content:
                st.markdown(content)



def display_response(response) -> dict | None:
    """
    Trích xuất và hiển thị phản hồi không streaming. Trả về dict message cho assistant.
    Gợi ý: Parse 'response.output', kiểm tra block.type ('reasoning' hoặc 'message').
    """
    # TODO 2.3/2.4 (Dưới giao diện): Lặp qua response.output để lấy content và reasoning_content
    # TODO 2.6: Hiển thị reasoning bằng st.expander('PROCESSING') và content bằng st.markdown
    # Trả về {"role": "assistant", "content": ..., "reasoning_content": ...}
    pass


def display_streaming_response(response_generator, stream_slot=None) -> dict | None:
    """
    Hiển thị streaming theo thời gian thực (text và reasoning). Trả về dict message cuối cùng.
    Gợi ý: 
    1. Khởi tạo reasoning_placeholder (st.empty) và text_placeholder (st.empty).
    2. Lặp qua response_generator, kiểm tra event.type để cập nhật text/reasoning. 
    3. Khi kết thúc (RESPONSE_COMPLETED), trả về message_dict để append vào history.
    """
    # TODO 3.4: Khởi tạo các placeholder cho reasoning và nội dung văn bản
    # TODO 3.5: Lắng nghe event.type == RESPONSE_REASONING_TEXT_DELTA để cập nhật reasoning_placeholder
    # TODO 3.6: Lắng nghe event.type == RESPONSE_OUTPUT_TEXT_DELTA để cập nhật text_placeholder
    # TODO 3.7: Trả về Assistant Message Dictionary hoàn chỉnh sau khi kết thúc stream
    pass
    Gợi ý: 
    1. Lặp qua 'response_generator'. 
    2. Nếu event.type là REASONING: cập nhật hiển thị trong expander 'PROCESSING'.
    3. Nếu event.type là OUTPUT: cập nhật nội dung tin nhắn Markdown.
    4. Trả về dict đầy đủ để append vào lịch sử sau khi stream xong.
    """
    # TODO: Dùng st.empty() (hoặc stream_slot) để tạo các vùng render linh hoạt
    # TODO: Khai báo biến tạm lưu content_response và reasoning_content_response
    # TODO: Lặp các event và cập nhật placeholder tương ứng
    # return {"role": "assistant", "content": ..., "reasoning_content": ...}
    pass
