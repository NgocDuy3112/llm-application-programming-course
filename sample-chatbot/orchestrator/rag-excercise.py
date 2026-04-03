"""
RAG (Retrieval-Augmented Generation) Module

Mô tả: Xử lý toàn bộ pipeline RAG cho chatbot:
  1. Đọc tài liệu (PDF, DOCX, TXT, MD)
  2. Chia nhỏ văn bản (chunking)
  3. Tạo embedding và lưu vào ChromaDB
  4. Tìm kiếm tài liệu liên quan (retrieval)
  5. Rerank kết quả bằng Cross-Encoder
"""

import os
import uuid
import tempfile
from logger import global_logger

import chromadb
from markitdown import MarkItDown
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SimpleRAG:
    """
    Class đơn giản thực hiện toàn bộ pipeline RAG.

    Workflow:
        1. add_documents() → đọc file → chunk → embed → lưu ChromaDB
        2. retrieve() → embed query → search ChromaDB → rerank → trả về context
    """

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        embedding_model_name: str = "AITeamVN/Vietnamese_Embedding_v2",
        cross_encoder_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        chroma_path: str = "./chroma_db",
        chunk_size: int = 1500,
        chunk_overlap: int = 200,
    ):
        global_logger.info(f"Initializing SimpleRAG: collection={collection_name}")

        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.cross_encoder = CrossEncoder(cross_encoder_model_name)

        os.makedirs(chroma_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=chromadb.Settings(allow_reset=True)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        self.markitdown = MarkItDown()

    # ================================================================
    # 1. ĐỌC TÀI LIỆU
    # ================================================================

    def load_document(self, file) -> str:
        """
        Đọc và chuyển đổi file upload sang Markdown (Streamlit UploadedFile).

        Workflow:
            1. Lưu file tạm ra ổ đĩa (markitdown cần file path)
            2. Dùng MarkItDown convert sang Markdown
            3. Xóa file tạm

        Hỗ trợ: .txt, .md, .pdf, .docx, .pptx, .xlsx, .html

        Args:
            file: Streamlit UploadedFile object (có .name và .read())

        Returns:
            str: Nội dung Markdown của file

        Gợi ý:
            - Dùng os.path.splitext(file.name)[1] để lấy đuôi file
            - Dùng tempfile.NamedTemporaryFile(delete=False, suffix=...) để tạo file tạm
            - Dùng self.markitdown.convert(path).text_content để lấy nội dung
            - Dùng os.unlink(path) trong finally để xóa file tạm
        """
        raise NotImplementedError("TODO: Implement load_document()")

    # ================================================================
    # 2. THÊM TÀI LIỆU VÀO KNOWLEDGE BASE
    # ================================================================

    def add_documents(self, files: list) -> int:
        """
        Pipeline: đọc files → chunk → embed → lưu vào ChromaDB.

        Args:
            files: Danh sách Streamlit UploadedFile objects

        Returns:
            int: Tổng số chunks đã thêm vào knowledge base

        Gợi ý (theo thứ tự):
            1. load_document(file) → content
            2. self.text_splitter.split_text(content) → chunks
            3. self.embedding_model.encode(chunks).tolist() → embeddings
            4. Tạo ids = [str(uuid.uuid4()) for _ in chunks]
            5. Tạo metadatas = [{"source": file.name, "chunk_index": i} ...]
            6. self.collection.add(ids, embeddings, documents, metadatas)
        """
        raise NotImplementedError("TODO: Implement add_documents()")

    # ================================================================
    # 3. TÌM KIẾM (VECTOR SEARCH)
    # ================================================================

    def search(self, query: str, top_k: int = 15) -> tuple[list[str], list[dict]]:
        """
        Tìm kiếm documents tương tự với query trong ChromaDB.

        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả tối đa cần lấy

        Returns:
            tuple[list[str], list[dict]]: (documents, metadatas)

        Gợi ý:
            - Embed query: self.embedding_model.encode([query]).tolist()
            - Query ChromaDB: self.collection.query(
                  query_embeddings=...,
                  n_results=min(top_k, self.doc_count()),
                  include=["documents", "metadatas"]
              )
            - Kết quả: results["documents"][0] và results["metadatas"][0]
        """
        if self.doc_count() == 0:
            return [], []

        raise NotImplementedError("TODO: Implement search()")

    # ================================================================
    # 4. RERANKING
    # ================================================================

    def rerank(self, query: str, documents: list[str], top_k: int = 6) -> list[str]:
        """
        Rerank kết quả search bằng Cross-Encoder để tăng độ chính xác.

        Args:
            query: Câu hỏi của người dùng
            documents: Danh sách documents từ bước search
            top_k: Số kết quả tốt nhất cần giữ lại

        Returns:
            list[str]: Documents đã sắp xếp lại theo relevance score

        Gợi ý:
            - Tạo pairs = [[query, doc] for doc in documents]
            - scores = self.cross_encoder.predict(pairs)
            - sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        """
        if not documents:
            return []

        raise NotImplementedError("TODO: Implement rerank()")

    # ================================================================
    # 5. RETRIEVE (SEARCH + RERANK + FORMAT)
    # ================================================================

    def retrieve(self, query: str, search_top_k: int = 15, rerank_top_k: int = 5) -> str:
        """
        Pipeline đầy đủ: search → rerank → format thành context string.

        Args:
            query: Câu hỏi của người dùng
            search_top_k: Số kết quả lấy từ vector search
            rerank_top_k: Số kết quả giữ lại sau reranking

        Returns:
            str: Context string với format:
                "[Tài liệu 1 — 📄 source.pdf]\nnội dung...\n\n---\n\n[Tài liệu 2 ...]..."

        Gợi ý:
            - Gọi self.search() → (documents, metadatas)
            - Rerank inline dùng indices để giữ docs và metas đồng bộ:
                pairs = [[query, doc] for doc in documents]
                scores = self.cross_encoder.predict(pairs)
                ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:rerank_top_k]
            - Format: f"[Tài liệu {i} — 📄 {source}]\n{doc}"
            - Join bằng "\n\n---\n\n"
        """
        raise NotImplementedError("TODO: Implement retrieve()")

    # ================================================================
    # 6. UTILITIES (ĐÃ IMPLEMENT SẴN)
    # ================================================================

    def doc_count(self) -> int:
        return self.collection.count()

    def list_sources(self) -> list[dict]:
        if self.collection.count() == 0:
            return []
        result = self.collection.get(include=["metadatas"])
        metadatas = result.get("metadatas", [])
        source_counts: dict[str, int] = {}
        for meta in metadatas:
            source = meta.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        return [
            {"source": src, "chunk_count": count}
            for src, count in sorted(source_counts.items())
        ]

    def delete_source(self, source_name: str) -> int:
        result = self.collection.get(where={"source": source_name}, include=[])
        ids_to_delete = result.get("ids", [])
        if not ids_to_delete:
            return 0
        self.collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def clear(self):
        if self.collection.count() > 0:
            all_ids = self.collection.get()["ids"]
            self.collection.delete(ids=all_ids)