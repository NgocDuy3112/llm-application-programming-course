"""
==========================================
PHẦN 2 — Kiểm tra Tools Integration
==========================================

Chạy sau khi hoàn thành các TODO trong orchestrator/tools.py:
    pytest tests/test_part2_tools.py -v

Lưu ý: test này KHÔNG cần Streamlit đang chạy.
st.session_state được mock bằng dict đơn giản.
"""

import sys
import os
import types
import pytest

# ---------------------------------------------------------------------------
# Mock `streamlit` trước khi import tools, để tránh lỗi thiếu môi trường ST
# ---------------------------------------------------------------------------
_mock_st = types.ModuleType("streamlit")
_session_state = {}
_mock_st.session_state = _session_state
sys.modules.setdefault("streamlit", _mock_st)


# ================================================================
# T1 — set_rag_instance() và _rag_instance
# ================================================================

class TestSetRagInstance:

    def test_set_rag_instance_does_not_raise(self):
        """set_rag_instance() không được raise NotImplementedError"""
        from orchestrator.tools import set_rag_instance
        try:
            set_rag_instance(object())
        except NotImplementedError:
            pytest.fail(
                "set_rag_instance() vẫn raise NotImplementedError — chưa implement TODO 1"
            )

    def test_rag_instance_stored_at_module_level(self):
        """Sau khi gọi set_rag_instance(x), module phải lưu x vào _rag_instance"""
        import orchestrator.tools as tools_module
        from orchestrator.tools import set_rag_instance

        sentinel = object()
        set_rag_instance(sentinel)
        assert getattr(tools_module, "_rag_instance", None) is sentinel, (
            "_rag_instance phải được gán bằng giá trị truyền vào"
        )

    def test_set_rag_instance_overwrites_previous(self):
        """Gọi set_rag_instance() lần 2 phải ghi đè giá trị cũ"""
        import orchestrator.tools as tools_module
        from orchestrator.tools import set_rag_instance

        obj1 = object()
        obj2 = object()
        set_rag_instance(obj1)
        set_rag_instance(obj2)
        assert tools_module._rag_instance is obj2, (
            "Lần gọi thứ 2 phải ghi đè _rag_instance"
        )


# ================================================================
# T2 — knowledge_base_search()
# ================================================================

class FakeRAG:
    """RAG stub để test knowledge_base_search() mà không cần model thật."""
    def __init__(self, doc_count=0, retrieve_result="kết quả tìm kiếm"):
        self._doc_count = doc_count
        self._retrieve_result = retrieve_result

    def doc_count(self):
        return self._doc_count

    def retrieve(self, query):
        return self._retrieve_result


class TestKnowledgeBaseSearch:

    def setup_method(self):
        """Reset session_state và _rag_instance trước mỗi test"""
        _session_state.clear()
        import orchestrator.tools as tools_module
        tools_module._rag_instance = None

    def test_returns_error_when_rag_not_set(self):
        """Phải trả về thông báo lỗi nếu _rag_instance là None"""
        from orchestrator.tools import knowledge_base_search
        result = knowledge_base_search("câu hỏi")
        assert "chưa được khởi tạo" in result.lower() or "error" in result.lower(), (
            "Phải trả về thông báo lỗi khi _rag_instance là None"
        )

    def test_returns_empty_message_when_kb_empty(self):
        """Phải trả về thông báo trống nếu KB không có documents"""
        from orchestrator.tools import set_rag_instance, knowledge_base_search
        set_rag_instance(FakeRAG(doc_count=0))
        result = knowledge_base_search("câu hỏi")
        assert "trống" in result.lower() or "empty" in result.lower(), (
            "Phải thông báo Knowledge base đang trống"
        )

    def test_returns_retrieve_result_when_kb_has_docs(self):
        """Phải trả về kết quả từ rag.retrieve() khi KB có dữ liệu"""
        from orchestrator.tools import set_rag_instance, knowledge_base_search
        expected = "nội dung tài liệu liên quan"
        set_rag_instance(FakeRAG(doc_count=5, retrieve_result=expected))
        result = knowledge_base_search("câu hỏi")
        assert result == expected, (
            "Phải trả về đúng kết quả từ rag.retrieve()"
        )

    def test_saves_result_to_session_state(self):
        """Kết quả phải được lưu vào st.session_state['last_retrieved_docs']"""
        from orchestrator.tools import set_rag_instance, knowledge_base_search
        expected = "context từ RAG"
        set_rag_instance(FakeRAG(doc_count=3, retrieve_result=expected))
        knowledge_base_search("câu hỏi")
        assert _session_state.get("last_retrieved_docs") == expected, (
            "Phải lưu kết quả vào st.session_state['last_retrieved_docs']"
        )

    def test_does_not_raise_not_implemented(self):
        """knowledge_base_search() không được raise NotImplementedError"""
        from orchestrator.tools import set_rag_instance, knowledge_base_search
        set_rag_instance(None)
        try:
            knowledge_base_search("câu hỏi")
        except NotImplementedError:
            pytest.fail(
                "knowledge_base_search() vẫn raise NotImplementedError — chưa implement TODO 2"
            )


# ================================================================
# T3 — AVAILABLE_FUNCTIONS và DEFAULT_TOOLS
# ================================================================

class TestToolRegistration:

    def test_knowledge_base_search_in_available_functions(self):
        """'knowledge_base_search' phải có mặt trong AVAILABLE_FUNCTIONS"""
        from orchestrator.tools import AVAILABLE_FUNCTIONS
        assert "knowledge_base_search" in AVAILABLE_FUNCTIONS, (
            "Phải thêm 'knowledge_base_search' vào AVAILABLE_FUNCTIONS (TODO 3)"
        )

    def test_available_functions_callable(self):
        """Giá trị của 'knowledge_base_search' trong AVAILABLE_FUNCTIONS phải callable"""
        from orchestrator.tools import AVAILABLE_FUNCTIONS
        fn = AVAILABLE_FUNCTIONS.get("knowledge_base_search")
        assert callable(fn), (
            "AVAILABLE_FUNCTIONS['knowledge_base_search'] phải là callable"
        )

    def test_knowledge_base_search_in_default_tools(self):
        """DEFAULT_TOOLS phải có tool spec cho 'knowledge_base_search'"""
        from orchestrator.tools import DEFAULT_TOOLS
        names = [t["function"]["name"] for t in DEFAULT_TOOLS]
        assert "knowledge_base_search" in names, (
            "Phải thêm tool spec 'knowledge_base_search' vào DEFAULT_TOOLS (TODO 3)"
        )

    def test_default_tools_spec_has_required_fields(self):
        """Tool spec của knowledge_base_search phải có đủ các trường bắt buộc"""
        from orchestrator.tools import DEFAULT_TOOLS
        spec = next(
            (t for t in DEFAULT_TOOLS if t["function"]["name"] == "knowledge_base_search"),
            None
        )
        assert spec is not None
        fn = spec["function"]
        assert "description" in fn and len(fn["description"]) > 0, (
            "Tool spec phải có 'description' không rỗng"
        )
        assert "parameters" in fn, "Tool spec phải có 'parameters'"
        params = fn["parameters"]
        assert "properties" in params, "'parameters' phải có 'properties'"
        assert "query" in params["properties"], (
            "'properties' phải có tham số 'query'"
        )

    def test_existing_tools_still_present(self):
        """Các tools cũ (tavily_search, get_current_date) vẫn phải còn trong DEFAULT_TOOLS"""
        from orchestrator.tools import DEFAULT_TOOLS, AVAILABLE_FUNCTIONS
        tool_names = [t["function"]["name"] for t in DEFAULT_TOOLS]
        assert "tavily_search" in tool_names
        assert "get_current_date" in tool_names
        assert "tavily_search" in AVAILABLE_FUNCTIONS
        assert "get_current_date" in AVAILABLE_FUNCTIONS
