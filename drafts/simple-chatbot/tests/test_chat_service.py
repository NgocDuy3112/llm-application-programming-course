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
    prompt = ChatService.summarize_conversation(history)
    assert isinstance(prompt, list)
    # Prompt should start with a system instruction and end with a user summarization instruction
    assert prompt[0]["role"] == "system"
    assert prompt[-1]["role"] == "user"
    assert "HÃY TÓM TẮT" in prompt[-1]["content"]
    # Conversation should be included in the prompt
    assert any(p.get("content") == "message 0" for p in prompt)


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
    class MockClient:
        def __init__(self):
            self.calls = []
            self.responses = ["api-summary", "final-response"]

        def create_response(self, **kwargs):
            self.calls.append(kwargs)
            return self.responses[len(self.calls) - 1]

        def create_structured_response(self, **kwargs):
            self.calls.append(kwargs)
            class R:
                def model_dump(self):
                    return {"ok": True}
            return R()

    client = MockClient()
    svc = ChatService(client)
    history = make_history(10)
    svc.create_response(
        mode="non-streaming",
        input_data=history,
        use_summarization=True,
    )
    # Two calls: one to summarize, one to get the final answer
    assert len(client.calls) == 2
    # First call is the summarization prompt
    summ_prompt = client.calls[0]["input"]
    assert isinstance(summ_prompt, list)
    assert summ_prompt[0]["role"] == "system"
    assert summ_prompt[-1]["role"] == "user"
    assert "HÃY TÓM TẮT" in summ_prompt[-1]["content"]
    # Second call includes system + summary + user
    final_inp = client.calls[1]["input"]
    assert isinstance(final_inp, list)
    assert final_inp[0]["role"] == "system"
    assert final_inp[1]["role"] == "system"
    assert "api-summary" in final_inp[1]["content"]
    assert final_inp[2]["role"] == "user"
    assert final_inp[2]["content"] == "message 9"


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


def test_create_response_uses_api_for_summarization():
    class MockClient:
        def __init__(self):
            self.calls = []
            self.responses = ["api-summary", "final-response"]

        def create_response(self, **kwargs):
            self.calls.append(kwargs)
            return self.responses[len(self.calls) - 1]

        def create_structured_response(self, **kwargs):
            self.calls.append(kwargs)
            class R:
                def model_dump(self):
                    return {"ok": True}
            return R()

    client = MockClient()
    svc = ChatService(client)
    history = make_history(10)
    svc.create_response(mode="non-streaming", input_data=history, use_summarization=True)
    # Two calls expected: one for summarization, one for final answer
    assert len(client.calls) == 2
    assert isinstance(client.calls[0]["input"], list)
    assert client.calls[0]["input"][0]["role"] == "system"
    assert client.calls[0]["input"][-1]["role"] == "user"
    assert "HÃY TÓM TẮT" in client.calls[0]["input"][-1]["content"]
    final_inp = client.calls[1]["input"]
    assert isinstance(final_inp, list)
    assert final_inp[0]["role"] == "system"
    assert final_inp[1]["role"] == "system"
    assert "api-summary" in final_inp[1]["content"]
    assert final_inp[2]["role"] == "user"
    assert final_inp[2]["content"] == "message 9"
