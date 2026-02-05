from src.services.chat_service import ChatService
from src.core.client import OpenAIStandardClient
from src.core.exceptions import ValidationError
from src.utils.settings import MAX_HISTORY_MESSAGES


class DummyClient:
    def __init__(self):
        self.last_kwargs = None

    def create_response(self, **kwargs):
        self.last_kwargs = kwargs
        return "dummy-response"

    def create_structured_response(self, **kwargs):
        self.last_kwargs = kwargs

        class R:
            def model_dump(self):
                return {"ok": True}

        return R()


def make_history(n):
    return [{"role": "user", "content": f"message {i}"} for i in range(n)]


def test_sliding_window_basic():
    history = make_history(20)
    out = ChatService.sliding_window(history, 5)
    assert len(out) == 5
    assert out == history[-5:]


def test_sliding_window_noop():
    history = make_history(3)
    out = ChatService.sliding_window(history, 10)
    assert out == history


def test_summarize_conversation_basic():
    history = make_history(3)
    out = ChatService.summarize_conversation(history)
    assert isinstance(out, list) and len(out) == 1
    assert out[0]["role"] == "system"
    assert "Tóm tắt cuộc hội thoại" in out[0]["content"]


def test_create_response_respects_sliding_window():
    client = DummyClient()
    svc = ChatService(client)
    history = make_history(30)
    svc.create_response(
        mode="non-streaming",
        input_data=history,
        use_sliding_window=True,
        max_history_messages=7,
    )
    assert client.last_kwargs is not None
    assert len(client.last_kwargs["input"]) == 7


def test_create_response_respects_summarization():
    client = DummyClient()
    svc = ChatService(client)
    history = make_history(10)
    svc.create_response(
        mode="non-streaming",
        input_data=history,
        use_summarization=True,
    )
    assert client.last_kwargs is not None
    inp = client.last_kwargs["input"]
    assert isinstance(inp, list)
    assert inp[0]["role"] == "system"
    assert "Tóm tắt cuộc hội thoại" in inp[0]["content"]


def test_create_response_conflicting_modes():
    client = DummyClient()
    svc = ChatService(client)
    history = make_history(4)
    try:
        svc.create_response(
            mode="non-streaming",
            input_data=history,
            use_sliding_window=True,
            use_summarization=True,
        )
        assert False, "Expected ValidationError when both modes are set"
    except ValidationError:
        assert True
