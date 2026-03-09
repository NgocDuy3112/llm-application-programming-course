import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

from ui.sidebar import sidebar
from ui.helpers import *
from service.chat import *

# Gợi ý: load_dotenv() từ .env file
load_dotenv(dotenv_path=".env", override=True)


def main():
    st.set_page_config(page_title="Advanced Chatbot", page_icon="🤖", layout="wide")
    st.title("Xây dựng chatbot đơn giản - Module 5")

    # TODO 1.7: Khởi tạo lịch sử hội thoại (gọi initialize_chat_history)
    # TODO 1.8: Nạp API Key qua settings.GROQ_API_KEY và khởi tạo OpenAI client
    
    initialize_chat_history()

    # Thêm sidebar (lưu ý sidebar() chỉ thiết lập widget, các giá trị lấy qua st.session_state)
    sidebar()

    # Gợi ý: Khởi tạo client OpenAI với GROQ_API_KEY
    client = OpenAI(
        api_key=os.getenv("OLLAMA_API_KEY"),
        base_url="https://ollama.com/v1"
    )

    # TODO: Khởi tạo ChatService phù hợp (ChatService, SlidingWindow, hoặc Summarization)
    # Dựa trên lựa chọn từ sidebar qua st.session_state["context_mode_widget"]
    chat_service = ChatService(client=client, history=st.session_state["chat_history"])

    # TODO: Hiển thị lịch sử chat (render_chat_history)
    render_chat_history(st.session_state["chat_history"])

    # Xử lý user input
    user_input = st.chat_input(
        placeholder="Nhập tin nhắn của bạn...",
        disabled=st.session_state.get("is_generating", False)
    )

    if user_input:
        st.session_state["is_generating"] = True
        # Gợi ý: Khi nhận input, gọi chat_service.response(...)
        # Kiểm tra stream_mode để gọi display_streaming_response hoặc display_response
        # Cập nhật phản hồi cuối cùng vào chat_history và gọi st.rerun() để hiển thị mới nhất
        st.session_state["is_generating"] = False
        st.rerun()



if __name__ == "__main__":
    main()
