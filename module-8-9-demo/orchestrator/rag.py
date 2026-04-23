# Khai báo module docstring - mô tả chức năng của module RAG
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

# Import os module để làm việc với paths và environment variables
import os
# Import uuid module để tạo unique IDs cho các chunks
import uuid
# Import tempfile module để tạo temporary files
import tempfile
# Import global_logger từ logger module để ghi log
from logger import global_logger

# Import chromadb - vector database để lưu trữ embeddings
import chromadb
# Import MarkItDown - công cụ convert nhiều định dạng file sang Markdown
from markitdown import MarkItDown
# Import pypdf để đọc PDF dưới dạng plain text
from pypdf import PdfReader
# Import python-docx để đọc DOCX dưới dạng plain text
from docx import Document as DocxDocument
# Import SentenceTransformer (embedding) và CrossEncoder (reranking) từ sentence-transformers
from sentence_transformers import SentenceTransformer, CrossEncoder
# Import RecursiveCharacterTextSplitter và MarkdownHeaderTextSplitter để chia nhỏ văn bản
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
# Import SearchEngine để xử lý toàn bộ logic tìm kiếm (vector, BM25, hybrid, rerank)
from orchestrator.search import SearchEngine


# Định nghĩa class SimpleRAG - class chính thực hiện toàn bộ pipeline RAG
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

    # Constructor của SimpleRAG class
    def __init__(
        self,
        collection_name: str ,  # Tên collection trong ChromaDB
        embedding_model_name: str ,  # Model embedding
        cross_encoder_model_name: str,  # Model reranking
        chroma_path: str = "./chroma_db",  # Đường dẫn lưu ChromaDB
        chunk_size: int = 1500,  # Kích thước mỗi chunk (ký tự)
        chunk_overlap: int = 200,  # Số ký tự chồng lấp giữa các chunk
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
        # Ghi log info: bắt đầu khởi tạo SimpleRAG
        global_logger.info(f"Initializing SimpleRAG: collection={collection_name}, embedding={embedding_model_name}")

        # ---- Embedding model ----
        # Dùng để chuyển text → vector (mảng số) để so sánh độ tương đồng
        # SentenceTransformer load model từ HuggingFace
        self.embedding_model = SentenceTransformer(embedding_model_name)
        # Ghi log debug: đã load embedding model
        global_logger.debug(f"Loaded embedding model: {embedding_model_name}")

        # ---- Cross-Encoder model (cho reranking) ----
        # Sau khi tìm được top-k kết quả, cross-encoder sẽ chấm điểm chính xác hơn
        # Cross-Encoder nhận cặp (query, document) và output score
        self.cross_encoder = CrossEncoder(cross_encoder_model_name)
        # Ghi log debug: đã load cross-encoder model
        global_logger.debug(f"Loaded cross-encoder model: {cross_encoder_model_name}")

        # ---- ChromaDB (vector database) ----
        # Lưu trữ embedding trên ổ đĩa, giữ lại giữa các lần restart
        
        # Tạo directory nếu chưa tồn tại
        os.makedirs(chroma_path, exist_ok=True)
        
        # Khởi tạo ChromaDB PersistentClient với path và settings
        # allow_reset=True cho phép reset collection khi cần
        self.chroma_client = chromadb.PersistentClient(path=chroma_path, settings=chromadb.Settings(allow_reset=True))
        
        # Get or create collection với name và metadata
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            # Metadata cấu hình sử dụng cosine similarity cho khoảng cách vectors
            metadata={"hnsw:space": "cosine"}  # Dùng cosine similarity
        )
        # Ghi log debug: ChromaDB đã được khởi tạo
        global_logger.debug(f"ChromaDB initialized at: {chroma_path}, collection: {collection_name}")

        # ---- Text Splitter ----
        # Chia văn bản dài thành các đoạn nhỏ để embedding hiệu quả hơn
        
        # Khởi tạo RecursiveCharacterTextSplitter (dùng cho plain text)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,  # Kích thước tối đa mỗi chunk
            chunk_overlap=chunk_overlap,  # Số ký tự overlap giữa các chunks
            length_function=len,  # Function để đo độ dài (dùng len())
            # Ưu tiên tách tại paragraph (\n\n) > dòng (\n) > câu (. ) > từ ( ) > ký tự ()
            separators=["\n\n", "\n", ". ", " ", ""],  # Ưu tiên tách tại paragraph > câu > từ
        )

        # Khởi tạo MarkdownHeaderTextSplitter (dùng cho Markdown mode)
        # Tách văn bản theo cấu trúc heading, mỗi section thành 1 chunk riêng
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
                ("#####", "Header 5"),
                ("######", "Header 6"),  
            ],
            strip_headers=False,  # Giữ lại dòng heading trong nội dung chunk
        )
        # Ghi log debug: text splitter đã được cấu hình
        global_logger.debug(f"Text splitters configured: chunk_size={chunk_size}, overlap={chunk_overlap}")

        # ---- MarkItDown converter ----
        # Chuyển đổi mọi định dạng file (PDF, DOCX, PPTX, ...) sang Markdown
        # giúp giữ nguyên cấu trúc heading, list, table trước khi chunking
        self.markitdown = MarkItDown()
        # Ghi log debug: MarkItDown đã được khởi tạo
        global_logger.debug("MarkItDown converter initialized")

        # ---- Search Engine ----
        # Xử lý toàn bộ logic tìm kiếm: vector, BM25, hybrid, rerank, retrieve
        self.search_engine = SearchEngine(
            embedding_model=self.embedding_model,
            cross_encoder=self.cross_encoder,
            collection=self.collection,
        )
        global_logger.debug("SearchEngine initialized")

    def set_keyword_extractor(self, adapter, model: str):
        """
        Cấu hình LLM để trích xuất keywords trước khi BM25 search.

        Args:
            adapter: BaseAdapter instance (GroqAdapter, OllamaAdapter, ...)
            model: Tên model dùng cho keyword extraction
        """
        self.search_engine.set_keyword_extractor(adapter, model)

    # ================================================================
    # 1. ĐỌC TÀI LIỆU
    # ================================================================

    # Method để đọc và convert file sang Markdown hoặc plain text
    def load_document(self, file, use_markdown: bool = True) -> str:
        """
        Đọc file upload và trả về nội dung dạng Markdown hoặc plain text.

        - use_markdown=True : Dùng MarkItDown convert file → Markdown rồi lưu
        - use_markdown=False: Đọc thẳng nội dung file (plain text, không qua MarkItDown)

        Hỗ trợ (plain text mode): .txt, .md, .html, .csv và các file text-based
        Hỗ trợ (markdown mode) : .txt, .md, .pdf, .docx, .pptx, .xlsx, .html, ...

        Args:
            file: Streamlit UploadedFile object (có .name và .read())
            use_markdown: True → MarkItDown → Markdown; False → plain text trực tiếp

        Returns:
            str: Nội dung file
        """
        # Lấy tên file từ uploaded file object
        file_name = file.name
        # Ghi log debug: đang load document với chế độ tương ứng
        global_logger.debug(f"Loading document: {file_name} (use_markdown={use_markdown})")

        # ---- CHế ĐỘ TẮT: dùng thư viện chuyên dụng extract text từ file ----
        if not use_markdown:
            suffix = os.path.splitext(file_name)[1].lower()

            if suffix == ".pdf":
                # Dùng pypdf để extract text từ PDF
                raw_bytes = file.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(raw_bytes)
                    tmp_path = tmp.name
                try:
                    reader = PdfReader(tmp_path)
                    content = "\n".join(page.extract_text() or "" for page in reader.pages)
                finally:
                    os.unlink(tmp_path)

            elif suffix == ".docx":
                # Dùng python-docx để extract text từ DOCX
                raw_bytes = file.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(raw_bytes)
                    tmp_path = tmp.name
                try:
                    doc = DocxDocument(tmp_path)
                    content = "\n".join(para.text for para in doc.paragraphs)
                finally:
                    os.unlink(tmp_path)

            else:
                # Các file text-based (.txt, .md, .csv, .html, ...): đọc trực tiếp
                raw_bytes = file.read()
                content = raw_bytes.decode("utf-8", errors="replace")

            global_logger.info(f"Read '{file_name}' as plain text: {len(content)} characters")
            return content

        # ---- CHế ĐỘ BẬT: dùng MarkItDown convert → Markdown ----
        suffix = os.path.splitext(file_name)[1]  # Lấy đuôi file (.pdf, .docx, ...)

        # Lưu vào temporary file vì markitdown cần đường dẫn file thật
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        try:
            # Chuyển đổi file sang Markdown dùng MarkItDown
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

    # Method để thêm nhiều documents vào knowledge base
    def add_documents(self, files: list, use_markdown: bool = True) -> int:
        """
        Pipeline: đọc files → chunk → embed → lưu vào ChromaDB.

        Args:
            files: Danh sách Streamlit UploadedFile objects
            use_markdown: True → giữ Markdown khi extract; False → plain text

        Returns:
            int: Tổng số chunks đã thêm vào knowledge base
        """
        # Biến đếm tổng số chunks đã thêm
        total_chunks = 0

        # Lặp qua từng file trong danh sách files
        for file in files:
            try:
                # Bước 1: Đọc nội dung file (Markdown hoặc plain text tùy use_markdown)
                content = self.load_document(file, use_markdown=use_markdown)
                
                # Kiểm tra nếu content rỗng (chỉ có whitespace)
                if not content.strip():
                    # Ghi log warning: file rỗng, bỏ qua
                    global_logger.warning(f"File '{file.name}' is empty, skipping")
                    # Bỏ qua file này, tiếp tục file tiếp theo
                    continue

                # Bước 2: Chia nhỏ văn bản thành các chunks
                if use_markdown:
                    # Markdown mode - 2 bước:
                    # Bước 2a: MarkdownHeaderTextSplitter tách theo cấu trúc heading
                    #          mỗi section (#, ##, ###) thành 1 Document riêng
                    header_docs = self.markdown_splitter.split_text(content)
                    # Bước 2b: Với mỗi section còn quá lớn (vượt chunk_size),
                    #          dùng text_splitter cắt tiếp → đảm bảo không có chunk khổng lồ
                    chunks = []
                    for doc in header_docs:
                        sub_chunks = self.text_splitter.split_text(doc.page_content)
                        chunks.extend(sub_chunks)
                    chunks = [c for c in chunks if c.strip()]
                else:
                    # Plain text mode: tách theo paragraph, câu, từ
                    chunks = self.text_splitter.split_text(content)
                # Ghi log info: số chunks đã tạo được từ file
                global_logger.info(f"Split '{file.name}' into {len(chunks)} chunks")

                # Kiểm tra nếu không có chunks nào
                if not chunks:
                    # Bỏ qua file này
                    continue

                # Bước 3: Tạo embedding cho từng chunk
                # encode() trả về numpy array, tolist() convert sang Python list
                embeddings = self.embedding_model.encode(chunks).tolist()

                # Bước 4: Tạo unique IDs và metadata cho mỗi chunk
                # uuid.uuid4() tạo UUID ngẫu nhiên, str() convert sang string
                ids = [str(uuid.uuid4()) for _ in chunks]
                # Tạo metadata list với source file name và chunk index
                metadatas = [{"source": file.name, "chunk_index": i} for i in range(len(chunks))]

                # Bước 5: Lưu vào ChromaDB
                # Collection.add() thêm documents với ids, embeddings, documents, và metadatas
                self.collection.add(
                    ids=ids,  # Danh sách unique IDs
                    embeddings=embeddings,  # Danh sách vectors embedding
                    documents=chunks,  # Danh sách text chunks
                    metadatas=metadatas,  # Danh sách metadata dicts
                )

                # Cộng dồn số chunks đã thêm
                total_chunks += len(chunks)
                # Ghi log info: đã thêm chunks từ file vào knowledge base
                global_logger.info(f"Added {len(chunks)} chunks from '{file.name}' to knowledge base")

            # Xử lý exception nếu có lỗi khi processing file
            except Exception as e:
                # Ghi log error với tên file và message lỗi
                global_logger.error(f"Error processing file '{file.name}': {str(e)}")
                # Re-raise exception để caller biết có lỗi
                raise e

        # Ghi log info: tổng số chunks đã thêm
        global_logger.info(f"Total chunks added: {total_chunks}")

        # Rebuild BM25 index sau khi thêm documents mới
        self.search_engine.build_bm25()
        
        # Trả về tổng số chunks
        return total_chunks

    # ================================================================
    # 3. TÌM KIẾM & RETRIEVE
    # ================================================================

    def retrieve(
        self,
        query: str,
        search_top_k: int = 15,
        rerank_top_k: int = 4,
        use_hybrid: bool = False,
        use_rerank: bool = True,
    ) -> str:
        """
        Pipeline đầy đủ: search → (rerank) → format context.
        Delegate toàn bộ cho SearchEngine.

        Args:
            query: Câu hỏi của người dùng
            search_top_k: Số kết quả lấy từ search
            rerank_top_k: Số kết quả giữ lại sau reranking
            use_hybrid: True → Hybrid (vector + BM25 + RRF); False → vector only
            use_rerank: True → dùng Cross-Encoder rerank; False → bỏ qua bước rerank

        Returns:
            str: Context string hoặc thông báo nếu không tìm thấy
        """
        return self.search_engine.retrieve(
            query,
            search_top_k=search_top_k,
            rerank_top_k=rerank_top_k,
            use_hybrid=use_hybrid,
            use_rerank=use_rerank,
        )

    # ================================================================
    # 4. UTILITIES
    # ================================================================

    # Method để lấy số lượng documents trong collection
    def doc_count(self) -> int:
        """Trả về số lượng chunks trong knowledge base."""
        # collection.count() trả về số documents trong collection
        return self.collection.count()

    # Method để lấy danh sách các source files
    def list_sources(self) -> list[dict]:
        """
        Trả về danh sách các file đã được thêm vào knowledge base.

        Returns:
            list[dict]: Mỗi phần tử gồm:
                - source (str): tên file
                - chunk_count (int): số chunks của file đó
        """
        # Kiểm tra nếu collection trống
        if self.collection.count() == 0:
            # Trả về list rỗng
            return []

        # Lấy tất cả documents với metadatas
        result = self.collection.get(include=["metadatas"])
        # Lấy metadatas từ result
        metadatas = result.get("metadatas", [])

        # Dictionary để đếm số chunks per source
        source_counts: dict[str, int] = {}
        
        # Lặp qua từng metadata
        for meta in metadatas:
            # Lấy source từ metadata, default là "Unknown"
            source = meta.get("source", "Unknown")
            # Increment count cho source này
            source_counts[source] = source_counts.get(source, 0) + 1

        # Trả về list của dicts với source và chunk_count
        # Sắp xếp theo source name
        return [
            {"source": src, "chunk_count": count}
            for src, count in sorted(source_counts.items())
        ]

    # Method để xóa tất cả chunks của một source file
    def delete_source(self, source_name: str) -> int:
        """
        Xóa tất cả chunks của một file cụ thể khỏi knowledge base.

        Args:
            source_name: Tên file cần xóa (khớp chính xác với metadata["source"])

        Returns:
            int: Số chunks đã xóa
        """
        # Ghi log info: đang xóa source
        global_logger.info(f"Deleting source: '{source_name}'")

        # Lấy tất cả documents với metadata filter theo source
        result = self.collection.get(
            where={"source": source_name},  # Filter: chỉ lấy documents có source này
            include=[],  # Không cần include data
        )
        # Lấy danh sách IDs của documents cần xóa
        ids_to_delete = result.get("ids", [])

        # Kiểm tra nếu không có IDs nào
        if not ids_to_delete:
            # Ghi log warning: không tìm thấy chunks
            global_logger.warning(f"No chunks found for source: '{source_name}'")
            # Trả về 0 (không xóa gì)
            return 0

        # Xóa documents khỏi collection bằng IDs
        self.collection.delete(ids=ids_to_delete)
        
        # Ghi log info: đã xóa thành công với số chunks
        global_logger.info(f"Deleted {len(ids_to_delete)} chunks from source: '{source_name}'")
        
        # Trả về số chunks đã xóa
        return len(ids_to_delete)

    # Method để xóa toàn bộ knowledge base
    def clear(self):
        """Xóa toàn bộ documents trong knowledge base (giữ nguyên collection)."""
        # Ghi log info: đang clear knowledge base
        global_logger.info("Clearing knowledge base")
        
        # Kiểm tra nếu collection có documents
        if self.collection.count() > 0:
            # Lấy tất cả IDs từ collection
            all_ids = self.collection.get()["ids"]
            # Xóa tất cả documents bằng IDs
            self.collection.delete(ids=all_ids)
        
        # Ghi log info: đã clear thành công
        global_logger.info("Knowledge base cleared successfully")
