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
# Import SentenceTransformer (embedding) và CrossEncoder (reranking) từ sentence-transformers
from sentence_transformers import SentenceTransformer, CrossEncoder
# Import RecursiveCharacterTextSplitter để chia nhỏ văn bản
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
        collection_name: str = "knowledge_base",  # Tên collection trong ChromaDB
        embedding_model_name: str = "AITeamVN/Vietnamese_Embedding_v2",  # Model embedding
        cross_encoder_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",  # Model reranking
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
        
        # Khởi tạo RecursiveCharacterTextSplitter để chia nhỏ văn bản
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,  # Kích thước tối đa mỗi chunk
            chunk_overlap=chunk_overlap,  # Số ký tự overlap giữa các chunks
            length_function=len,  # Function để đo độ dài (dùng len())
            # Ưu tiên tách tại paragraph (\n\n) > dòng (\n) > câu (. ) > từ ( ) > ký tự ()
            separators=["\n\n", "\n", ". ", " ", ""],  # Ưu tiên tách tại paragraph > câu > từ
        )
        # Ghi log debug: text splitter đã được cấu hình
        global_logger.debug(f"Text splitters configured: chunk_size={chunk_size}, overlap={chunk_overlap}")

        # ---- MarkItDown converter ----
        # Chuyển đổi mọi định dạng file (PDF, DOCX, PPTX, ...) sang Markdown
        # giúp giữ nguyên cấu trúc heading, list, table trước khi chunking
        self.markitdown = MarkItDown()
        # Ghi log debug: MarkItDown đã được khởi tạo
        global_logger.debug("MarkItDown converter initialized")

    # ================================================================
    # 1. ĐỌC TÀI LIỆU
    # ================================================================

    # Method để đọc và convert file sang Markdown
    def load_document(self, file) -> str:
        """
        Đọc file upload và trả về nội dung dạng Markdown (dùng MarkItDown).

        Hỗ trợ: .txt, .md, .pdf, .docx, .pptx, .xlsx, .html, ...

        Args:
            file: Streamlit UploadedFile object (có .name và .read())

        Returns:
            str: Nội dung file dạng Markdown
        """
        # Lấy tên file từ uploaded file object
        file_name = file.name
        # Ghi log debug: đang load document
        global_logger.debug(f"Loading document: {file_name}")

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
    def add_documents(self, files: list) -> int:
        """
        Pipeline: đọc files → chunk → embed → lưu vào ChromaDB.

        Args:
            files: Danh sách Streamlit UploadedFile objects

        Returns:
            int: Tổng số chunks đã thêm vào knowledge base
        """
        # Biến đếm tổng số chunks đã thêm
        total_chunks = 0

        # Lặp qua từng file trong danh sách files
        for file in files:
            try:
                # Bước 1: Đọc nội dung file và convert sang Markdown
                content = self.load_document(file)
                
                # Kiểm tra nếu content rỗng (chỉ có whitespace)
                if not content.strip():
                    # Ghi log warning: file rỗng, bỏ qua
                    global_logger.warning(f"File '{file.name}' is empty, skipping")
                    # Bỏ qua file này, tiếp tục file tiếp theo
                    continue

                # Bước 2: Chia nhỏ văn bản thành các chunks
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
        
        # Trả về tổng số chunks
        return total_chunks

    # ================================================================
    # 3. TÌM KIẾM (RETRIEVAL)
    # ================================================================

    # Method để search documents trong ChromaDB
    def search(self, query: str, top_k: int = 15) -> tuple[list[str], list[dict]]:
        """
        Tìm kiếm documents tương tự với query trong ChromaDB.

        Cách hoạt động:
            1. Embed query thành vector
            2. Tìm top_k vectors gần nhất trong ChromaDB (cosine similarity)
            3. Trả về danh sách text và metadata tương ứng

        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả tối đa cần lấy

        Returns:
            tuple[list[str], list[dict]]: Danh sách đoạn văn bản và metadata (source, ...)
        """
        # Kiểm tra nếu knowledge base không có documents nào
        if self.doc_count() == 0:
            # Ghi log debug: knowledge base trống
            global_logger.debug("Knowledge base is empty, returning empty results")
            # Trả về 2 list rỗng
            return [], []

        # Ghi log debug: đang search với query (50 ký tự đầu tiên)
        global_logger.debug(f"Searching knowledge base for: '{query[:50]}...'")

        # Embed query thành vector
        # encode() nhận list các strings, trả về numpy array
        # tolist() convert sang Python list để truyền vào ChromaDB
        query_embedding = self.embedding_model.encode([query]).tolist()

        # Tìm kiếm trong ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,  # Vector embedding của query
            # Số kết quả cần lấy, không vượt quá số documents có sẵn
            n_results=min(top_k, self.doc_count()),  # Không lấy nhiều hơn số doc có
            # Bao gồm documents (text) và metadatas trong kết quả
            include=["documents", "metadatas"],
        )

        # Lấy danh sách documents từ results
        # results.get() trả về dict, ["documents"] là list của list, [0] lấy list đầu tiên
        documents = results.get("documents", [[]])[0]
        # Lấy danh sách metadatas từ results
        metadatas = results.get("metadatas", [[]])[0]
        
        # Ghi log debug: số kết quả tìm được
        global_logger.debug(f"Found {len(documents)} results from vector search")
        
        # Trả về tuple (documents, metadatas)
        return documents, metadatas

    # ================================================================
    # 4. RERANKING
    # ================================================================

    # Method để rerank documents dùng Cross-Encoder
    def rerank(
        self,
        query: str,
        documents: list[str],
        metadatas: list[dict] | None = None,
        top_k: int = 6,
    ) -> tuple[list[str], list[dict]]:
        """
        Rerank kết quả search bằng Cross-Encoder để tăng độ chính xác.

        Cross-Encoder nhận cặp (query, document) và cho điểm relevance.
        Chính xác hơn cosine similarity nhưng chậm hơn → chỉ dùng trên top-k nhỏ.

        Args:
            query: Câu hỏi của người dùng
            documents: Danh sách documents từ bước search
            metadatas: Danh sách metadata tương ứng với documents (optional)
            top_k: Số kết quả tốt nhất cần giữ lại

        Returns:
            tuple[list[str], list[dict]]: Documents và metadatas đã được sắp xếp lại theo relevance
        """
        # Kiểm tra nếu không có documents
        if not documents:
            # Trả về 2 list rỗng
            return [], []

        # Chuẩn hóa metadatas: nếu None thì tạo list rỗng tương ứng
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Ghi log debug: đang rerank với số documents và top_k
        global_logger.debug(f"Reranking {len(documents)} documents, keeping top {top_k}")

        # Tạo cặp (query, document) cho cross-encoder
        # List comprehension tạo list của lists: [[query, doc1], [query, doc2], ...]
        pairs = [[query, doc] for doc in documents]

        # Cross-encoder chấm điểm từng cặp
        # predict() trả về numpy array của scores
        scores = self.cross_encoder.predict(pairs)

        # Sắp xếp indices theo score giảm dần và lấy top_k
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        # Lấy documents và metadatas theo thứ tự đã rerank
        reranked_docs  = [documents[i] for i in ranked_indices]
        reranked_metas = [metadatas[i] for i in ranked_indices]

        # Ghi log debug: reranking hoàn tất với top scores
        top_scores = sorted(scores, reverse=True)[:top_k]
        global_logger.debug(f"Reranking complete, top scores: {[f'{s:.3f}' for s in top_scores]}")

        # Trả về tuple (documents, metadatas) đã rerank
        return reranked_docs, reranked_metas

    # ================================================================
    # 5. RETRIEVE (KẾT HỢP SEARCH + RERANK)
    # ================================================================

    # Method chính để retrieve context từ knowledge base
    def retrieve(self, query: str, search_top_k: int = 15, rerank_top_k: int = 4) -> str:
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
        # Ghi log info: bắt đầu retrieve với query
        global_logger.info(f"RAG retrieve for query: '{query}...'")

        # Bước 1: Vector search (with metadata)
        # Gọi method search() để lấy documents và metadatas
        documents, metadatas = self.search(query, top_k=search_top_k)

        # Kiểm tra nếu không có documents
        if not documents:
            # Trả về message thông báo không tìm thấy
            return "Không tìm thấy thông tin liên quan trong knowledge base."

        # Bước 2: Rerank (giữ metadata đồng bộ với documents)
        # Gọi self.rerank() với cả documents lẫn metadatas để giữ đồng bộ
        reranked_docs, reranked_metas = self.rerank(query, documents, metadatas, top_k=rerank_top_k)

        # Bước 3: Format thành context string (có source)
        
        # List để chứa các phần context
        context_parts = []
        
        # Lặp qua documents và metadatas với index (bắt đầu từ 1)
        for i, (doc, meta) in enumerate(zip(reranked_docs, reranked_metas), 1):
            # Lấy source từ metadata, default là "Unknown"
            source = meta.get("source", "Unknown") if meta else "Unknown"
            # Tạo context part với header chứa số thứ tự và source
            context_parts.append(f"[Tài liệu {i} — 📄 {source}]\n{doc}")

        # Join các context parts với delimiter "\n\n---\n\n"
        context = "\n\n---\n\n".join(context_parts)
        
        # Ghi log info: retrieve hoàn tất với số documents và độ dài context
        global_logger.info(f"RAG retrieve complete: {len(reranked_docs)} documents, {len(context)} chars")
        
        # Trả về context string
        return context

    # ================================================================
    # 6. UTILITIES
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
