"""
RAG (Retrieval-Augmented Generation) Module

Mô tả: Xử lý toàn bộ pipeline RAG cho chatbot:
  1. Đọc tài liệu (PDF, DOCX, TXT, MD)
  2. Chia nhỏ văn bản (chunking)
  3. Tạo embedding và lưu vào ChromaDB
  4. Tìm kiếm tài liệu liên quan (retrieval)
  5. Rerank kết quả bằng Cross-Encoder

Kiến trúc / Dependencies:
  - chromadb: Vector database để lưu trữ và tìm kiếm embedding
  - sentence-transformers: Tạo embedding + Cross-Encoder reranking
  - langchain-text-splitters: Chia nhỏ văn bản thông minh
  - pypdf, python-docx: Đọc file PDF và DOCX
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
    
    Attributes:
        embedding_model: Model để tạo vector embedding từ text
        cross_encoder: Model để rerank kết quả tìm kiếm
        collection: ChromaDB collection lưu trữ documents
        text_splitter: Công cụ chia nhỏ văn bản
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
        """
        Khởi tạo RAG pipeline.
        
        Args:
            collection_name: Tên collection trong ChromaDB
            embedding_model_name: Tên model embedding (từ HuggingFace)
            cross_encoder_model_name: Tên model cross-encoder để rerank
            chroma_path: Đường dẫn lưu ChromaDB trên ổ đĩa
            chunk_size: Kích thước mỗi chunk (số ký tự)
            chunk_overlap: Số ký tự chồng lấp giữa các chunk
        """
        global_logger.info(f"Initializing SimpleRAG: collection={collection_name}, embedding={embedding_model_name}")

        # ---- Embedding model ----
        # Dùng để chuyển text → vector (mảng số) để so sánh độ tương đồng
        self.embedding_model = SentenceTransformer(embedding_model_name)
        global_logger.debug(f"Loaded embedding model: {embedding_model_name}")

        # ---- Cross-Encoder model (cho reranking) ----
        # Sau khi tìm được top-k kết quả, cross-encoder sẽ chấm điểm chính xác hơn
        self.cross_encoder = CrossEncoder(cross_encoder_model_name)
        global_logger.debug(f"Loaded cross-encoder model: {cross_encoder_model_name}")

        # ---- ChromaDB (vector database) ----
        # Lưu trữ embedding trên ổ đĩa, giữ lại giữa các lần restart
        os.makedirs(chroma_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path, settings=chromadb.Settings(allow_reset=True))
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Dùng cosine similarity
        )
        global_logger.debug(f"ChromaDB initialized at: {chroma_path}, collection: {collection_name}")

        # ---- Text Splitter ----
        # Chia văn bản dài thành các đoạn nhỏ để embedding hiệu quả hơn
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],  # Ưu tiên tách tại paragraph > câu > từ
        )
        global_logger.debug(f"Text splitter configured: chunk_size={chunk_size}, overlap={chunk_overlap}")

        # ---- MarkItDown converter ----
        # Chuyển đổi mọi định dạng file (PDF, DOCX, PPTX, ...) sang Markdown
        # giúp giữ nguyên cấu trúc heading, list, table trước khi chunking
        self.markitdown = MarkItDown()
        global_logger.debug("MarkItDown converter initialized")

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
        
        Hỗ trợ: .txt, .md, .pdf, .docx, .pptx, .xlsx, .html, ...
        
        Args:
            file: Streamlit UploadedFile object (có .name và .read())
            
        Returns:
            str: Nội dung Markdown của file
        """
        file_name = file.name
        suffix = os.path.splitext(file_name)[1]  # Lấy đuôi file (.pdf, .docx, ...)
        global_logger.debug(f"Loading document: {file_name}")

        # Lưu vào file tạm vì markitdown cần đường dẫn file thật
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        try:
            # Chuyển đổi sang Markdown
            result = self.markitdown.convert(tmp_path)
            content = result.text_content
            global_logger.info(f"Converted '{file_name}' to Markdown: {len(content)} characters")
        except Exception as e:
            global_logger.error(f"MarkItDown failed for '{file_name}': {str(e)}")
            raise ValueError(f"Không thể đọc file '{file_name}': {str(e)}")
        finally:
            # Xóa file tạm dù thành công hay lỗi
            os.unlink(tmp_path)

        return content

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
        """
        total_chunks = 0

        for file in files:
            try:
                # Bước 1: Đọc nội dung file
                content = self.load_document(file)
                if not content.strip():
                    global_logger.warning(f"File '{file.name}' is empty, skipping")
                    continue

                # Bước 2: Chia nhỏ văn bản thành các chunks
                chunks = self.text_splitter.split_text(content)
                global_logger.info(f"Split '{file.name}' into {len(chunks)} chunks")

                if not chunks:
                    continue

                # Bước 3: Tạo embedding cho từng chunk
                embeddings = self.embedding_model.encode(chunks).tolist()

                # Bước 4: Tạo unique IDs và metadata cho mỗi chunk
                ids = [str(uuid.uuid4()) for _ in chunks]
                metadatas = [{"source": file.name, "chunk_index": i} for i in range(len(chunks))]

                # Bước 5: Lưu vào ChromaDB
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=metadatas,
                )

                total_chunks += len(chunks)
                global_logger.info(f"Added {len(chunks)} chunks from '{file.name}' to knowledge base")

            except Exception as e:
                global_logger.error(f"Error processing file '{file.name}': {str(e)}")
                raise e

        global_logger.info(f"Total chunks added: {total_chunks}")
        return total_chunks

    # ================================================================
    # 3. TÌM KIẾM (RETRIEVAL)
    # ================================================================

    def search(self, query: str, top_k: int = 15) -> list[str]:
        """
        Tìm kiếm documents tương tự với query trong ChromaDB.
        
        Cách hoạt động:
            1. Embed query thành vector
            2. Tìm top_k vectors gần nhất trong ChromaDB (cosine similarity)
            3. Trả về danh sách text tương ứng
        
        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả tối đa cần lấy
            
        Returns:
            list[str]: Danh sách đoạn văn bản liên quan
        """
        if self.doc_count() == 0:
            global_logger.debug("Knowledge base is empty, returning empty results")
            return []

        global_logger.debug(f"Searching knowledge base for: '{query[:50]}...'")

        # Embed query thành vector
        query_embedding = self.embedding_model.encode([query]).tolist()

        # Tìm kiếm trong ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.doc_count()),  # Không lấy nhiều hơn số doc có
        )

        documents = results.get("documents", [[]])[0]
        global_logger.debug(f"Found {len(documents)} results from vector search")
        return documents

    # ================================================================
    # 4. RERANKING
    # ================================================================

    def rerank(self, query: str, documents: list[str], top_k: int = 6) -> list[str]:
        """
        Rerank kết quả search bằng Cross-Encoder để tăng độ chính xác.
        
        Cross-Encoder nhận cặp (query, document) và cho điểm relevance.
        Chính xác hơn cosine similarity nhưng chậm hơn → chỉ dùng trên top-k nhỏ.
        
        Args:
            query: Câu hỏi của người dùng
            documents: Danh sách documents từ bước search
            top_k: Số kết quả tốt nhất cần giữ lại
            
        Returns:
            list[str]: Danh sách documents đã được sắp xếp lại theo relevance
        """
        if not documents:
            return []

        global_logger.debug(f"Reranking {len(documents)} documents, keeping top {top_k}")

        # Tạo cặp (query, document) cho cross-encoder
        pairs = [[query, doc] for doc in documents]

        # Cross-encoder chấm điểm từng cặp
        scores = self.cross_encoder.predict(pairs)

        # Sắp xếp theo điểm giảm dần, lấy top_k
        scored_docs = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        reranked = [doc for _, doc in scored_docs[:top_k]]

        global_logger.debug(f"Reranking complete, top scores: {[f'{s:.3f}' for s, _ in scored_docs[:top_k]]}")
        return reranked

    # ================================================================
    # 5. RETRIEVE (KẾT HỢP SEARCH + RERANK)
    # ================================================================

    def retrieve(self, query: str, search_top_k: int = 15, rerank_top_k: int = 5) -> str:
        """
        Pipeline đầy đủ: search → rerank → format thành context string.
        
        Đây là method chính được gọi bởi tool knowledge_base_search.
        
        Args:
            query: Câu hỏi của người dùng
            search_top_k: Số kết quả lấy từ vector search
            rerank_top_k: Số kết quả giữ lại sau reranking
            
        Returns:
            str: Context string chứa các đoạn văn bản liên quan, 
                 hoặc thông báo nếu không tìm thấy
        """
        global_logger.info(f"RAG retrieve for query: '{query}...'")

        # Bước 1: Vector search
        documents = self.search(query, top_k=search_top_k)

        if not documents:
            return "Không tìm thấy thông tin liên quan trong knowledge base."

        # Bước 2: Rerank
        reranked_docs = self.rerank(query, documents, top_k=rerank_top_k)

        # Bước 3: Format thành context string
        context_parts = []
        for i, doc in enumerate(reranked_docs, 1):
            context_parts.append(f"[Tài liệu {i}]\n{doc}")

        context = "\n\n---\n\n".join(context_parts)
        global_logger.info(f"RAG retrieve complete: {len(reranked_docs)} documents, {len(context)} chars")
        return context

    # ================================================================
    # 6. UTILITIES
    # ================================================================

    def doc_count(self) -> int:
        """Trả về số lượng chunks trong knowledge base."""
        return self.collection.count()

    def list_sources(self) -> list[dict]:
        """
        Trả về danh sách các file đã được thêm vào knowledge base.

        Returns:
            list[dict]: Mỗi phần tử gồm:
                - source (str): tên file
                - chunk_count (int): số chunks của file đó
        """
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
        """
        Xóa tất cả chunks của một file cụ thể khỏi knowledge base.

        Args:
            source_name: Tên file cần xóa (khớp chính xác với metadata["source"])

        Returns:
            int: Số chunks đã xóa
        """
        global_logger.info(f"Deleting source: '{source_name}'")

        result = self.collection.get(
            where={"source": source_name},
            include=[],
        )
        ids_to_delete = result.get("ids", [])

        if not ids_to_delete:
            global_logger.warning(f"No chunks found for source: '{source_name}'")
            return 0

        self.collection.delete(ids=ids_to_delete)
        global_logger.info(f"Deleted {len(ids_to_delete)} chunks from source: '{source_name}'")
        return len(ids_to_delete)

    def clear(self):
        """Xóa toàn bộ documents trong knowledge base (giữ nguyên collection)."""
        global_logger.info("Clearing knowledge base")
        if self.collection.count() > 0:
            all_ids = self.collection.get()["ids"]
            self.collection.delete(ids=all_ids)
        global_logger.info("Knowledge base cleared successfully")
