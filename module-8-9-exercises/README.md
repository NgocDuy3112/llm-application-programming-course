# Bài tập Buổi 7 — Tích hợp RAG vào ứng dụng chatbot

## Cấu trúc project

```
sample-chatbot-exercise/
├── app.py                      ← Entry point (có TODO)
├── custom_types.py             ← Enums: Provider, ToolChoice, ...
├── logger.py                   ← Global logger
├── requirements.txt
├── pyproject.toml
├── .env.sample                 ← Copy thành .env và điền API keys
├── model/
│   └── adapter.py              ← GroqAdapter, OllamaAdapter (đã implement)
├── orchestrator/
│   ├── engine.py               ← FullChatbotEngine (đã implement)
│   ├── memory.py               ← SlidingWindowMemory (đã implement)
│   ├── rag.py                  ← SimpleRAG (có TODO)
│   └── tools.py                ← Function calling tools (có TODO)
└── ui/
    ├── chat_interface.py       ← Chat UI (có TODO)
    └── sidebar.py              ← Sidebar UI (có TODO)
```

## Cài đặt

```bash
# Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Cài dependencies
pip install -r requirements.txt

# Cấu hình API keys
copy .env.sample .env
# Điền GROQ_API_KEY và TAVILY_API_KEY vào .env
```

## Chạy ứng dụng

```bash
streamlit run app.py
```

## Danh sách TODO

| File | TODO | Mô tả |
|------|------|-------|
| `app.py` | TODO 1 | Implement `get_rag()` factory |
| `app.py` | TODO 2 | Khởi tạo RAG trong `main()` |
| `orchestrator/rag.py` | load_document | Đọc file → Markdown |
| `orchestrator/rag.py` | add_documents | Pipeline embed → ChromaDB |
| `orchestrator/rag.py` | search | Vector search ChromaDB |
| `orchestrator/rag.py` | rerank | Cross-encoder reranking |
| `orchestrator/rag.py` | retrieve | Pipeline đầy đủ |
| `orchestrator/tools.py` | TODO 1 | Khai báo `_rag_instance` + `set_rag_instance()` |
| `orchestrator/tools.py` | TODO 2 | Implement `knowledge_base_search()` |
| `orchestrator/tools.py` | TODO 3 | Đăng ký tool vào `AVAILABLE_FUNCTIONS` và `DEFAULT_TOOLS` |
| `ui/chat_interface.py` | TODO 1 | Implement `_render_retrieved_docs()` |
| `ui/chat_interface.py` | TODO 2 | Hiển thị docs trong history loop |
| `ui/chat_interface.py` | TODO 3 | Hiển thị docs sau reply mới |
| `ui/sidebar.py` | TODO 1-5 | Knowledge Base section |
