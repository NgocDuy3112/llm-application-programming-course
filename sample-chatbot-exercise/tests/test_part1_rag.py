"""
==========================================
PHẦN 1 — Kiểm tra RAG Components
==========================================

Chạy sau khi hoàn thành các TODO trong orchestrator/rag.py:
    pytest tests/test_part1_rag.py -v

Thứ tự test phản ánh thứ tự implement:
    T1: load_document()
    T2: add_documents()
    T3: search()
    T4: rerank()
    T5: retrieve()
"""

import pytest


# ================================================================
# T1 — load_document()
# ================================================================

class TestLoadDocument:

    def test_load_txt_returns_string(self, rag, txt_file):
        """load_document() phải trả về str không rỗng với file .txt"""
        result = rag.load_document(txt_file)
        assert isinstance(result, str), "Kết quả phải là str"
        assert len(result) > 0, "Nội dung không được rỗng"

    def test_load_txt_contains_content(self, rag, txt_file):
        """Nội dung trả về phải chứa từ khóa từ file gốc"""
        result = rag.load_document(txt_file)
        assert "Python" in result, "Nội dung phải chứa text từ file gốc"

    def test_load_md_returns_string(self, rag, md_file):
        """load_document() phải hoạt động với file .md"""
        result = rag.load_document(md_file)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_md_contains_content(self, rag, md_file):
        """Nội dung .md phải chứa text từ file gốc"""
        result = rag.load_document(md_file)
        assert "chatbot" in result.lower() or "streamlit" in result.lower(), (
            "Nội dung phải chứa text từ file md gốc"
        )


# ================================================================
# T2 — add_documents()
# ================================================================

class TestAddDocuments:

    def test_add_single_file_returns_positive_count(self, rag, txt_file):
        """add_documents() với 1 file phải trả về số chunks > 0"""
        rag.clear()
        count = rag.add_documents([txt_file])
        assert isinstance(count, int), "Phải trả về int"
        assert count > 0, "Phải có ít nhất 1 chunk được thêm vào"

    def test_doc_count_increases_after_add(self, rag, txt_file):
        """doc_count() phải tăng sau khi add_documents()"""
        rag.clear()
        assert rag.doc_count() == 0
        rag.add_documents([txt_file])
        assert rag.doc_count() > 0, "doc_count() phải > 0 sau khi add"

    def test_add_multiple_files(self, rag, txt_file, md_file):
        """add_documents() với nhiều file phải add tất cả"""
        rag.clear()
        count = rag.add_documents([txt_file, md_file])
        assert count > 0
        assert rag.doc_count() == count, "doc_count() phải bằng tổng số chunks trả về"

    def test_list_sources_after_add(self, rag, txt_file, md_file):
        """list_sources() phải chứa tên cả 2 files sau khi add"""
        rag.clear()
        rag.add_documents([txt_file, md_file])
        sources = [s["source"] for s in rag.list_sources()]
        assert "sample.txt" in sources, "sample.txt phải có trong sources"
        assert "guide.md" in sources, "guide.md phải có trong sources"


# ================================================================
# T3 — search()
# ================================================================

class TestSearch:

    @pytest.fixture(autouse=True)
    def populate(self, rag, txt_file, md_file):
        """Đảm bảo KB có dữ liệu trước mỗi test trong class này"""
        rag.clear()
        rag.add_documents([txt_file, md_file])

    def test_search_returns_tuple(self, rag):
        """search() phải trả về tuple (list, list)"""
        result = rag.search("Python")
        assert isinstance(result, tuple) and len(result) == 2, (
            "search() phải trả về tuple có 2 phần tử"
        )
        docs, metas = result
        assert isinstance(docs, list)
        assert isinstance(metas, list)

    def test_search_returns_results(self, rag):
        """search() với query liên quan phải trả về ít nhất 1 kết quả"""
        docs, metas = rag.search("Python")
        assert len(docs) > 0, "Phải có ít nhất 1 document kết quả"

    def test_search_docs_and_metas_same_length(self, rag):
        """docs và metadatas phải có độ dài bằng nhau"""
        docs, metas = rag.search("RAG")
        assert len(docs) == len(metas), "docs và metas phải có cùng số phần tử"

    def test_search_metas_have_source(self, rag):
        """Mỗi metadata phải có trường 'source'"""
        _, metas = rag.search("chatbot")
        for meta in metas:
            assert "source" in meta, "Mỗi metadata phải có key 'source'"

    def test_search_empty_kb_returns_empty(self, rag):
        """search() trên KB rỗng phải trả về ([], [])"""
        rag.clear()
        docs, metas = rag.search("bất kỳ")
        assert docs == [] and metas == []

    def test_search_top_k_respected(self, rag, txt_file, md_file):
        """search() không được trả về nhiều hơn top_k kết quả"""
        rag.add_documents([txt_file, md_file])
        docs, _ = rag.search("Python", top_k=2)
        assert len(docs) <= 2, "Số kết quả không được vượt quá top_k"


# ================================================================
# T4 — rerank()
# ================================================================

class TestRerank:

    def test_rerank_returns_list(self, rag):
        """rerank() phải trả về list"""
        docs = ["Python là ngôn ngữ lập trình.", "RAG kết hợp retrieval và generation."]
        result = rag.rerank("Python", docs)
        assert isinstance(result, list), "rerank() phải trả về list"

    def test_rerank_empty_input_returns_empty(self, rag):
        """rerank() với list rỗng phải trả về list rỗng"""
        result = rag.rerank("query", [])
        assert result == []

    def test_rerank_top_k_limits_output(self, rag):
        """rerank() không được trả về nhiều hơn top_k phần tử"""
        docs = [f"Tài liệu số {i} về chủ đề lập trình." for i in range(10)]
        result = rag.rerank("lập trình", docs, top_k=3)
        assert len(result) <= 3, "Số kết quả không được vượt quá top_k"

    def test_rerank_output_is_subset_of_input(self, rag):
        """rerank() chỉ được trả về các docs có trong input"""
        docs = [
            "Python là ngôn ngữ lập trình phổ biến.",
            "ChromaDB là vector database.",
            "RAG tăng độ chính xác của LLM.",
        ]
        result = rag.rerank("Python và RAG", docs, top_k=2)
        for doc in result:
            assert doc in docs, f"Output '{doc[:30]}...' không có trong input"

    def test_rerank_most_relevant_first(self, rag):
        """Doc liên quan nhất phải được xếp đầu tiên"""
        docs = [
            "Hôm nay thời tiết đẹp, trời nắng.",        # ít liên quan
            "Python là ngôn ngữ AI phổ biến nhất.",     # rất liên quan
        ]
        result = rag.rerank("Python AI lập trình", docs, top_k=2)
        assert "Python" in result[0], (
            "Document liên quan nhất phải được xếp đầu tiên"
        )


# ================================================================
# T5 — retrieve()
# ================================================================

class TestRetrieve:

    @pytest.fixture(autouse=True)
    def populate(self, rag, txt_file, md_file):
        rag.clear()
        rag.add_documents([txt_file, md_file])

    def test_retrieve_returns_string(self, rag):
        """retrieve() phải trả về str"""
        result = rag.retrieve("Python")
        assert isinstance(result, str), "retrieve() phải trả về str"

    def test_retrieve_not_empty(self, rag):
        """retrieve() với query liên quan phải trả về nội dung không rỗng"""
        result = rag.retrieve("Python")
        assert len(result) > 0

    def test_retrieve_format_contains_doc_header(self, rag):
        """Kết quả phải chứa header dạng '[Tài liệu N — 📄 ...]'"""
        result = rag.retrieve("Python")
        assert "📄" in result, "Format phải chứa emoji 📄"
        assert "Tài liệu" in result, "Format phải chứa 'Tài liệu'"

    def test_retrieve_format_contains_separator(self, rag):
        """Các chunks phải được phân cách bằng '\\n\\n---\\n\\n' nếu có nhiều hơn 1"""
        result = rag.retrieve("Python RAG chatbot", rerank_top_k=3)
        chunks = result.split("\n\n---\n\n")
        assert len(chunks) >= 1, "Phải có ít nhất 1 chunk"

    def test_retrieve_format_source_in_header(self, rag):
        """Tên file nguồn phải xuất hiện trong header của context"""
        result = rag.retrieve("Python")
        assert "sample.txt" in result or "guide.md" in result, (
            "Tên file nguồn phải xuất hiện trong context"
        )

    def test_retrieve_respects_rerank_top_k(self, rag):
        """Số chunks trả về không được vượt quá rerank_top_k"""
        result = rag.retrieve("lập trình", rerank_top_k=2)
        chunks = result.split("\n\n---\n\n")
        assert len(chunks) <= 2, "Số chunks không được vượt quá rerank_top_k"
