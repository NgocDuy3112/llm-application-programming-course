import os
import tempfile

import streamlit as st

from src.services.ollama_chat import OllamaChatClient
from src.core.rag import IngestAndRetrievalEngine



THINKING_PROCESS_DISPLAY_STRING = "🧠 Quá trình suy luận"


def _chain_first(first_item, iterator):
    yield first_item
    yield from iterator


def stream(response, spinner_text: str) -> str:
    response_iter = iter(response)
    with st.spinner(spinner_text):
        try:
            first_chunk = next(response_iter)
        except StopIteration:
            first_chunk = None

    if first_chunk is None:
        st.markdown("")
        return ""

    thinking_expander = st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False)
    thinking_ph = thinking_expander.empty()
    message_ph = st.empty()
    full_text = ""
    full_reasoning = ""

    for chunk in _chain_first(first_chunk, response_iter):
        ctype = chunk.get("type") if isinstance(chunk, dict) else "text"
        content = chunk.get("content") if isinstance(chunk, dict) else str(chunk)
        if ctype == "reasoning":
            full_reasoning += content
            thinking_ph.markdown(full_reasoning)
        else:
            full_text += content
            message_ph.markdown(full_text + "▌")

    if full_reasoning:
        thinking_ph.markdown(full_reasoning)
    message_ph.markdown(full_text)
    return full_text


def sidebar():
    with st.sidebar:
        embedding_model = st.sidebar.selectbox(
            "Chọn mô hình mã hoá văn bản",
            options=[
                "all-MiniLM-L6-v2",
                "paraphrase-multilingual-MiniLM-L12-v2"
            ]
        )
        chunk_size = st.sidebar.slider(
            "Kích thước đoạn văn bản (chunk size)",
            min_value=100,
            max_value=2000,
            value=1000,
            step=100
        )
        chunk_overlap = st.sidebar.slider(
            "Độ chồng lắp đoạn văn bản (chunk overlap)",
            min_value=0,
            max_value=500,
            value=200,
            step=10
        )
        chat_model = st.sidebar.selectbox(
            "Chọn mô hình chat",
            options=[
                "qwen3:4b",
                "gemma3:1b"
            ]
        )
        temperature = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
        )

        max_output_tokens = st.sidebar.slider(
            "Số tokens tối đa",
            min_value=1,
            max_value=2048,
            value=512,
            step=1,
        )
        custom_instructions = st.sidebar.text_area(
            "Chỉ dẫn tùy chỉnh (tùy chọn)",
            value="",
            height=200,
        )
        ollama_client = OllamaChatClient(model=chat_model)
        key = f"rag_engine:{embedding_model}"
        rag_engine = st.session_state.setdefault(
            key, 
            IngestAndRetrievalEngine(
                embedding_model=embedding_model, 
                persist_directory="./chromadb", 
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )
        )

        st.sidebar.divider()
        st.sidebar.subheader("Tải tài liệu")
        uploaded_docx = st.sidebar.file_uploader(
            "Upload file .docx để ingest",
            type=["docx"],
            accept_multiple_files=False,
        )
        if uploaded_docx is not None:
            st.sidebar.caption(f"Đã chọn: {uploaded_docx.name}")
            if st.sidebar.button("Ingest tài liệu", type="primary"):
                with st.sidebar.spinner("Đang ingest..."):
                    try:
                        uploads_dir = os.path.join("data", "uploads")
                        os.makedirs(uploads_dir, exist_ok=True)

                        original_name = os.path.basename(uploaded_docx.name).replace("/", "_").replace("\\", "_")
                        base, ext = os.path.splitext(original_name)
                        ext = ext or ".docx"

                        saved_path = os.path.join(uploads_dir, base + ext)
                        if os.path.exists(saved_path):
                            i = 1
                            while True:
                                candidate = os.path.join(uploads_dir, f"{base}_{i}{ext}")
                                if not os.path.exists(candidate):
                                    saved_path = candidate
                                    break
                                i += 1

                        with open(saved_path, "wb") as f:
                            f.write(uploaded_docx.getbuffer())

                        st.session_state["last_uploaded_docx_path"] = saved_path
                        rag_engine.ingest_docx(saved_path, collection_name="documents")
                        st.sidebar.caption(f"Đã lưu tại: {saved_path}")
                        st.sidebar.success("Ingest thành công")
                    except Exception as e:
                        st.sidebar.error(f"Ingest thất bại: {e}")

    state = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "max_output_tokens": max_output_tokens,
        "custom_instructions": custom_instructions,
        "temperature": temperature,
    }
    return ollama_client, rag_engine, state



def main():
    st.title("RAG Chatbot với Ollama, Sentence Transformers và ChromaDB")
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { width: 420px; min-width: 420px; }
        .css-1d391kg { width: 420px; }
        /* shift main content to avoid overlap */
        main { margin-left: 440px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Get session state history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "streaming_mode" not in st.session_state:
        st.session_state["streaming_mode"] = True
    ollama_client, rag_engine, state = sidebar()
    # Render existing chat history in main area
    for msg in st.session_state.get("chat_history", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # show a thinking expander above each assistant message (collapsed)
        with st.chat_message(role):
            if role == "assistant":
                with st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False):
                    st.write("")
            st.markdown(content)
    user_input = st.chat_input("Type your message here...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        max_output_tokens = state["max_output_tokens"]
        temperature = state["temperature"]
        custom_instructions = state["custom_instructions"]
        retriveved_documents = rag_engine.retrieve(user_input, collection_name="documents", n_results=5)
        input_messages = st.session_state["chat_history"]
        if retriveved_documents:
            docs_contents = "Tài liệu:\n\n".join(
                [f"{doc.content}" for doc in retriveved_documents]
            )
            input_messages.append(
                {
                    "role": "system",
                    "content": f"Sử dụng các tài liệu sau để trả lời câu hỏi của người dùng:\n\n{docs_contents}"
                }
            )
        spinner_text = "Đang suy nghĩ..."
        response = ollama_client.create_response(
            input=input_messages,
            stream=True,
            instructions=custom_instructions,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
        with st.chat_message("assistant"):
            full_text = stream(response, spinner_text)
            if full_text == "":
                st.session_state["chat_history"].append({"role": "assistant", "content": ""})
                return

        # store only assistant message in history (do not store reasoning)
        st.session_state["chat_history"].append({"role": "assistant", "content": full_text})


if __name__ == "__main__":
    main()