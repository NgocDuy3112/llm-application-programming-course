# Module 6-7: Xây Dựng Chatbot với Function Calling và Context Management

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 Tổng Quan

Đây là một ứng dụng chatbot demo được xây dựng trong khuôn khổ khóa học **Lập Trình Ứng Dụng LLM**. Ứng dụng này minh họa các khái niệm cốt lõi trong việc xây dựng chatbot với:

- **Multi-Provider Support**: Hỗ trợ cả cloud (Groq) và local (Ollama) LLM providers
- **Function Calling**: Tích hợp tools để tìm kiếm web và lấy ngày hiện tại
- **Context Management**: Quản lý lịch sử hội thoại với sliding window strategy
- **Modern UI**: Giao diện Streamlit thân thiện và dễ sử dụng

## 🏗️ Kiến Trúc Hệ Thống

```
module-6-7/
├── app.py                    # Entry point - Streamlit application
├── custom_types.py          # Types và enums (Provider, ContextManagementMode, ToolChoice)
├── logger.py                # Logging system với rotation
├── pyproject.toml           # Project configuration (Poetry)
├── requirements.txt         # Python dependencies
├── model/
│   ├── __init__.py
│   └── adapter.py          # BaseAdapter, GroqAdapter, OllamaAdapter
├── orchestrator/
│   ├── __init__.py
│   ├── engine.py           # ChatbotEngine - orchestration logic
│   ├── memory.py           # SlidingWindowMemory - context management
│   └── tools.py            # Function definitions (tavily_search, get_current_date)
└── ui/
    ├── __init__.py
    ├── sidebar.py          # Settings sidebar UI
    └── chat_interface.py   # Main chat UI
```

## 🎯 Các Tính Năng Chính

### 1. Multi-Provider LLM Support

| Provider | Loại | API Endpoint | Ưu điểm |
|----------|------|--------------|---------|
| **Groq** | Cloud | `https://api.groq.com/openai/v1` | Tốc độ cao, không cần setup |
| **Ollama** | Local | `http://localhost:11434/v1` | Riêng tư, offline, free |

### 2. Context Management Modes

- **OFF**: Không lưu lịch sử - mỗi message xử lý độc lập
- **SLIDING_WINDOW**: Giữ N cặp user-assistant messages gần nhất
  - Cấu hình được số lượng turns (mặc định: 5)
  - Giúp kiểm soát độ dài context và chi phí API

### 3. Function Calling

Hệ thống tích hợp sẵn 2 tools:

| Tool | Mô tả | Parameters |
|------|-------|------------|
| `tavily_search` | Tìm kiếm web qua Tavily API | `query: str` |
| `get_current_date` | Trả về ngày hiện tại | Không có |

### 4. UI Components

**Sidebar Controls:**
- Chọn LLM provider (Groq/Ollama)
- Chọn model cụ thể
- Điều chỉnh temperature (0.0-1.0)
- Set max output tokens
- Cấu hình system prompt
- Chọn chế độ context management
- Bật/tắt function calling

**Chat Interface:**
- Hiển thị lịch sử hội thoại
- Xử lý input từ user
- Hiển thị response từ assistant
- Ẩn các internal reasoning blocks (<think>...</think>)

## 🚀 Cài Đặt và Chạy

### Yêu cầu

- Python 3.12+
- pip hoặc poetry

### Cài đặt

```bash
# Clone repository
git clone <repository-url>
cd llm-application-programming-course

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
# hoặc
poetry install
```

### Cấu hình Environment Variables

Tạo file `.env` ở root project:

```env
# Groq API (nếu dùng cloud)
GROQ_API_KEY=your_groq_api_key_here

# Tavily API (cho function calling)
TAVILY_API_KEY=your_tavily_api_key_here
```

### Chạy Ứng dụng

```bash
# Với Streamlit
streamlit run app.py

# Hoặc với poetry
poetry run streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501` để sử dụng chatbot.

## 📝 Bài Tập (Exercises)

Ứng dụng này được thiết kế như một bộ công cụ học tập với các bài tập thực hành:

### Bài Tập 1: LLM Adapter
- **BT1-Groq**: Implement `GroqAdapter._initialize_client()`
- **BT1-Ollama**: Implement `OllamaAdapter._initialize_client()`

### Bài Tập 2: System Prompt
- **BT2**: Thêm system_prompt vào messages trong `ChatbotEngine.response()`

### Bài Tập 3: Context Management
- **BT3a**: Implement `SlidingWindowMemory.add()` và `get_messages()`
- **BT3b**: Tích hợp SlidingWindowMemory vào engine

### Bài Tập 4: Function Calling
- **BT4a**: Định nghĩa tools theo OpenAI format trong `DEFAULT_TOOLS`
- **BT4b**: Implement vòng lặp function calling với tool execution

### Bài Tập 5: Guardrail và Orchestration
- **BT5**: Thêm max_iterations guardrail (≤8) và chỉ lưu final message

## 🔧 Công Nghệ Sử Dụng

| Công nghệ | Mục đích |
|-----------|----------|
| **Streamlit** | Web UI framework |
| **OpenAI SDK** | OpenAI-compatible API client |
| **Pydantic** | Data validation và settings management |
| **PyYAML** | Configuration management |
| **Tavily Python** | Web search API client |
| **RotatingFileHandler** | Log rotation |

## 📚 Cấu Trúc Code

### Custom Types (`custom_types.py`)

```python
Provider = Enum("Provider", ["GROQ", "OLLAMA"])
ContextManagementMode = Enum("ContextManagementMode", ["OFF", "SLIDING_WINDOW"])
ToolChoice = Enum("ToolChoice", ["NONE", "AUTO"])
```

### Adapter Pattern (`model/adapter.py`)

```
BaseAdapter (ABC)
├── GroqAdapter  → Groq API
└── OllamaAdapter → Local Ollama
```

### Orchestrator Pattern (`orchestrator/`)

```
ChatbotEngine
├── adapter: BaseAdapter
├── memory: SlidingWindowMemory
├── tools: list[dict]
└── response() → orchestration logic
```

## 🤝 Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

Dự án này được cấp phép theo MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 👨‍🏫 Tác Giả

Dự án được xây dựng trong khuôn khổ khóa học **Lập Trình Ứng Dụng LLM** tại [TTTH](https://ttth.edu.vn/).

## 🙏 Lời Cảm Ơn

- Groq team cho API access nhanh chóng
- Ollama team cho local LLM platform
- Streamlit team cho framework UI tuyệt vời
- Tavily cho search API chất lượng

---

**Chúc bạn học tập và xây dựng thật tốt! 🎓✨**
