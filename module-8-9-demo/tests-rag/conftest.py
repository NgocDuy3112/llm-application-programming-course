"""
conftest.py — Shared fixtures và sys.path setup cho toàn bộ test suite.
"""
import sys
import os
import shutil
import pytest

# Thêm project root vào sys.path để import được các module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ================================================================
# Mock Streamlit UploadedFile
# ================================================================

class FakeUploadedFile:
    """
    Mock Streamlit UploadedFile để dùng trong tests mà không cần chạy Streamlit.
    """
    def __init__(self, name: str, content: bytes):
        self.name = name
        self._content = content

    def read(self) -> bytes:
        return self._content


# ================================================================
# Fixtures dùng chung
# ================================================================

TEST_CHROMA_DIR = os.path.join(os.path.dirname(__file__), "_test_chroma_db")


@pytest.fixture(scope="module")
def rag():
    """
    Tạo SimpleRAG instance dùng chung cho cả module test.
    Dùng chroma_path riêng để tránh ảnh hưởng dữ liệu thật.
    """
    from orchestrator.rag import SimpleRAG
    instance = SimpleRAG(
        collection_name="test_collection",
        chroma_path=TEST_CHROMA_DIR,
    )
    instance.clear()   # bắt đầu từ trạng thái sạch
    yield instance
    # Dọn dẹp sau khi module test xong
    instance.clear()


@pytest.fixture(scope="module")
def txt_file():
    """File .txt đơn giản chứa nội dung tiếng Việt."""
    content = (
        "Python là ngôn ngữ lập trình bậc cao, dễ đọc và dễ học.\n"
        "Python được dùng rộng rãi trong lĩnh vực Data Science, AI và Web.\n\n"
        "LLM (Large Language Model) là các mô hình ngôn ngữ lớn được huấn luyện "
        "trên lượng dữ liệu khổng lồ.\n"
        "GPT, Llama, Gemini là các ví dụ nổi tiếng về LLM.\n\n"
        "RAG (Retrieval-Augmented Generation) là kỹ thuật kết hợp tìm kiếm tài liệu "
        "với sinh văn bản để tăng độ chính xác của LLM."
    )
    return FakeUploadedFile("sample.txt", content.encode("utf-8"))


@pytest.fixture(scope="module")
def md_file():
    """File .md chứa nội dung markdown."""
    content = (
        "# Hướng dẫn sử dụng chatbot\n\n"
        "## Cài đặt\n"
        "Chạy lệnh `pip install -r requirements.txt` để cài dependencies.\n\n"
        "## Sử dụng\n"
        "Điền API key vào file `.env` rồi chạy `streamlit run app.py`.\n\n"
        "## Tính năng\n"
        "- Hỗ trợ nhiều provider: Groq, Ollama\n"
        "- Tích hợp RAG với ChromaDB\n"
        "- Function calling với Tavily search\n"
    )
    return FakeUploadedFile("guide.md", content.encode("utf-8"))
