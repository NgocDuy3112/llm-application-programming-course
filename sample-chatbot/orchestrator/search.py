"""
Search Engine Module

Mô tả: Xử lý toàn bộ pipeline tìm kiếm cho RAG:
  1. Vector search (dense retrieval) — dùng ChromaDB + embedding model
  2. BM25 search (sparse retrieval) — keyword-based, dùng rank_bm25
  3. Hybrid search — kết hợp 2 phương pháp trên qua Reciprocal Rank Fusion (RRF)
  4. Reranking — dùng Cross-Encoder để chấm điểm lại kết quả
  5. Retrieve — pipeline đầy đủ: search → rerank → format context

Kiến trúc / Dependencies:
  - chromadb: Vector database để query embedding
  - sentence-transformers: Embedding model + Cross-Encoder reranking
  - rank_bm25: BM25Okapi cho keyword search
"""

from logger import global_logger
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from custom_types import ToolChoice


class SearchEngine:
    """
    Class xử lý các phương pháp tìm kiếm cho RAG pipeline.

    Nhận vào embedding_model, cross_encoder và ChromaDB collection từ SimpleRAG.
    Không tự load model — chỉ nhận references để tránh duplicate.

    Attributes:
        embedding_model: SentenceTransformer để encode query
        cross_encoder: CrossEncoder để rerank kết quả
        collection: ChromaDB collection để vector search
        _bm25_index: BM25Okapi index (rebuild sau mỗi lần thêm document)
        _bm25_docs: list chunks tương ứng với BM25 index
        _bm25_metas: list metadatas tương ứng
    """

    def __init__(self, embedding_model, cross_encoder: CrossEncoder, collection):
        """
        Khởi tạo SearchEngine.

        Args:
            embedding_model: SentenceTransformer instance từ SimpleRAG
            cross_encoder: CrossEncoder instance từ SimpleRAG
            collection: ChromaDB collection instance từ SimpleRAG
        """
        self.embedding_model = embedding_model
        self.cross_encoder = cross_encoder
        self.collection = collection

        # BM25 state — được rebuild sau mỗi add_documents()
        self._bm25_index = None
        self._bm25_docs: list[str] = []
        self._bm25_metas: list[dict] = []

        # Keyword extraction LLM — được set từ bên ngoài qua set_keyword_extractor()
        self._keyword_adapter = None
        self._keyword_model: str | None = None

        global_logger.debug("SearchEngine initialized")

    # ================================================================
    # 1. BUILD BM25 INDEX
    # ================================================================

    def build_bm25(self):
        """
        Lấy toàn bộ chunks từ ChromaDB và xây dựng lại BM25 index.
        Gọi sau mỗi lần add_documents() hoặc delete_source() để giữ đồng bộ.
        """
        result = self.collection.get(include=["documents", "metadatas"])
        self._bm25_docs = result.get("documents", [])
        self._bm25_metas = result.get("metadatas", [])

        if not self._bm25_docs:
            self._bm25_index = None
            global_logger.debug("BM25 index cleared (no documents)")
            return

        # Tokenize bằng whitespace split đơn giản
        tokenized = [doc.lower().split() for doc in self._bm25_docs]
        self._bm25_index = BM25Okapi(tokenized)
        global_logger.debug(f"BM25 index built with {len(self._bm25_docs)} documents")

    # ================================================================
    # 2. KEYWORD EXTRACTION (LLM)
    # ================================================================

    def set_keyword_extractor(self, adapter, model: str):
        """
        Cấu hình LLM adapter để extract keywords trước khi BM25 search.

        Args:
            adapter: BaseAdapter instance (GroqAdapter, OllamaAdapter, ...)
            model: Tên model dùng cho keyword extraction
        """
        self._keyword_adapter = adapter
        self._keyword_model = model
        global_logger.debug(f"Keyword extractor configured: model={model}")

    def extract_keywords(self, query: str) -> str:
        """
        Dùng LLM để trích xuất keywords từ câu hỏi người dùng.

        Loại bỏ stopwords, câu hỏi phụ, giữ lại các từ khóa quan trọng
        để BM25 search chính xác hơn.

        Args:
            query: Câu hỏi gốc của người dùng

        Returns:
            str: Chuỗi keywords đã trích xuất (fallback về query gốc nếu lỗi)
        """
        if self._keyword_adapter is None or self._keyword_model is None:
            return query

        prompt = (
            "Extract the important search keywords from the following user query. "
            "Remove stopwords, filler words, and question words. "
            "Return ONLY the keywords separated by spaces. No explanation, no punctuation.\n\n"
            f"Query: {query}\n"
            "Keywords:"
        )

        try:
            response = self._keyword_adapter.response(
                model=self._keyword_model,
                messages=[{"role": "user", "content": prompt}],
                tools=None,
                tool_choice=ToolChoice.NONE,
                temperature=0.0,
                max_tokens=100,
            )
            keywords = response.choices[0].message.content.strip()
            global_logger.info(f"Extracted keywords: '{keywords}' from query: '{query[:60]}'")
            return keywords if keywords else query
        except Exception as e:
            global_logger.warning(f"Keyword extraction failed: {e}, using raw query")
            return query

    # ================================================================
    # 3. VECTOR SEARCH (DENSE)
    # ================================================================

    def vector_search(self, query: str, top_k: int = 15) -> tuple[list[str], list[dict]]:
        """
        Tìm kiếm dense retrieval bằng cosine similarity trong ChromaDB.

        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả tối đa

        Returns:
            tuple[list[str], list[dict]]: documents và metadatas
        """
        if self.collection.count() == 0:
            global_logger.debug("Collection empty, skipping vector search")
            return [], []

        global_logger.debug(f"Vector search: '{query[:50]}...'")
        query_embedding = self.embedding_model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        global_logger.debug(f"Vector search found {len(documents)} results")
        return documents, metadatas

    # ================================================================
    # 4. BM25 SEARCH (SPARSE)
    # ================================================================

    def bm25_search(self, query: str, top_k: int = 15) -> tuple[list[str], list[dict]]:
        """
        Tìm kiếm keyword-based bằng BM25 (sparse retrieval).

        Nếu đã cấu hình keyword extractor (LLM), sẽ trích xuất keywords
        từ query trước khi search để loại bỏ stopwords và noise.

        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả tối đa

        Returns:
            tuple[list[str], list[dict]]: documents và metadatas theo thứ tự BM25 score
        """
        if not self._bm25_index or not self._bm25_docs:
            global_logger.debug("BM25 index empty, skipping BM25 search")
            return [], []

        # Dùng LLM extract keywords nếu có adapter, ngược lại dùng raw query
        search_query = self.extract_keywords(query)
        global_logger.debug(f"BM25 search: '{search_query[:50]}...'")
        tokenized_query = search_query.lower().split()
        scores = self._bm25_index.get_scores(tokenized_query)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        documents = [self._bm25_docs[i] for i in top_indices]
        metadatas = [self._bm25_metas[i] if i < len(self._bm25_metas) else {} for i in top_indices]

        global_logger.debug(f"BM25 search found {len(documents)} results")
        return documents, metadatas

    # ================================================================
    # 5. HYBRID SEARCH (VECTOR + BM25 + RRF)
    # ================================================================

    def hybrid_search(
        self, query: str, top_k: int = 15, rrf_k: int = 60
    ) -> tuple[list[str], list[dict]]:
        """
        Kết hợp vector search + BM25 bằng Reciprocal Rank Fusion (RRF).

        RRF score = 1/(rrf_k + rank_vector) + 1/(rrf_k + rank_bm25)
        Document xuất hiện ở cả 2 danh sách được boost điểm cao hơn.

        Args:
            query: Câu hỏi của người dùng
            top_k: Số kết quả cuối cùng cần trả về
            rrf_k: Hằng số RRF (thường là 60)

        Returns:
            tuple[list[str], list[dict]]: documents và metadatas sau khi RRF
        """
        global_logger.debug(f"Hybrid search: '{query[:50]}...'")

        vec_docs, vec_metas = self.vector_search(query, top_k=top_k)
        bm25_docs, bm25_metas = self.bm25_search(query, top_k=top_k)

        # Map text → metadata để tra cứu nhanh
        doc_meta_map: dict[str, dict] = {}
        for doc, meta in zip(vec_docs, vec_metas):
            doc_meta_map[doc] = meta
        for doc, meta in zip(bm25_docs, bm25_metas):
            if doc not in doc_meta_map:
                doc_meta_map[doc] = meta

        # Tính RRF score
        rrf_scores: dict[str, float] = {}
        for rank, doc in enumerate(vec_docs):
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + 1.0 / (rrf_k + rank + 1)
        for rank, doc in enumerate(bm25_docs):
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + 1.0 / (rrf_k + rank + 1)

        # Sắp xếp theo RRF score giảm dần
        sorted_docs = sorted(rrf_scores, key=lambda d: rrf_scores[d], reverse=True)[:top_k]
        sorted_metas = [doc_meta_map.get(doc, {}) for doc in sorted_docs]

        global_logger.debug(f"Hybrid search returned {len(sorted_docs)} results after RRF")
        return sorted_docs, sorted_metas

    # ================================================================
    # 6. RERANKING
    # ================================================================

    def rerank(
        self,
        query: str,
        documents: list[str],
        metadatas: list[dict],
        top_k: int = 5,
    ) -> tuple[list[str], list[dict]]:
        """
        Rerank documents bằng Cross-Encoder, trả về cả documents lẫn metadatas đã sắp xếp.

        Args:
            query: Câu hỏi của người dùng
            documents: Danh sách documents từ bước search
            metadatas: Danh sách metadatas tương ứng
            top_k: Số kết quả tốt nhất cần giữ lại

        Returns:
            tuple[list[str], list[dict]]: documents và metadatas đã rerank
        """
        if not documents:
            return [], []

        global_logger.debug(f"Reranking {len(documents)} documents, keeping top {top_k}")
        pairs = [[query, doc] for doc in documents]
        scores = self.cross_encoder.predict(pairs)

        # Sắp xếp indices theo score giảm dần
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        reranked_docs = [documents[i] for i in ranked_indices]
        reranked_metas = [metadatas[i] if i < len(metadatas) else {} for i in ranked_indices]

        top_scores = [f"{scores[i]:.3f}" for i in ranked_indices]
        global_logger.debug(f"Reranking complete, top scores: {top_scores}")
        return reranked_docs, reranked_metas

    # ================================================================
    # 7. RETRIEVE — PIPELINE ĐẦY ĐỦ
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
        Pipeline đầy đủ: search → (rerank) → format thành context string.

        Args:
            query: Câu hỏi của người dùng
            search_top_k: Số kết quả lấy từ search
            rerank_top_k: Số kết quả giữ lại sau reranking
            use_hybrid: True → Hybrid (vector + BM25 + RRF); False → vector only
            use_rerank: True → dùng Cross-Encoder rerank; False → bỏ qua bước rerank

        Returns:
            str: Context string chứa các đoạn văn bản liên quan,
                 hoặc thông báo nếu không tìm thấy
        """
        global_logger.info(
            f"Retrieve (hybrid={use_hybrid}, rerank={use_rerank}) for: '{query[:60]}...'")

        # Bước 1: Search
        if use_hybrid:
            documents, metadatas = self.hybrid_search(query, top_k=search_top_k)
        else:
            documents, metadatas = self.vector_search(query, top_k=search_top_k)

        if not documents:
            return "Không tìm thấy thông tin liên quan trong knowledge base."

        # Bước 2: Rerank (tuỳ chọn)
        if use_rerank:
            final_docs, final_metas = self.rerank(
                query, documents, metadatas, top_k=rerank_top_k
            )
        else:
            # Không rerank — cắt thẳng top rerank_top_k từ kết quả search
            final_docs = documents[:rerank_top_k]
            final_metas = metadatas[:rerank_top_k]
            global_logger.debug(f"Reranking skipped, using top {len(final_docs)} search results")

        # Bước 3: Format context string
        context_parts = []
        for i, (doc, meta) in enumerate(zip(final_docs, final_metas), 1):
            source = meta.get("source", "Unknown") if meta else "Unknown"
            context_parts.append(f"[Tài liệu {i} — 📄 {source}]\n{doc}")

        context = "\n\n---\n\n".join(context_parts)
        global_logger.info(
            f"Retrieve complete: {len(final_docs)} docs, {len(context)} chars"
        )
        return context
