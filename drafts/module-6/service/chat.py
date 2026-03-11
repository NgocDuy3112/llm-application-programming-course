import json
import time
import uuid
from types import SimpleNamespace
from typing import Any

from openai import OpenAI

from logger import ChatbotLogger
from service.custom_tools import DEFAULT_TOOLS, get_current_date, tavily_search
from settings import LLMProvider
from streaming_types import OpenAIResponseAPIStreamingState


logger = ChatbotLogger.get_logger("chat_service")


class ChatService:
    DEFAULT_INSTRUCTIONS = """
    Bạn là một trợ lý ảo thông minh và hữu ích, luôn cố gắng cung cấp câu trả lời chính xác và đầy đủ nhất cho người dùng.
    Bạn được cung cấp một số thông tin về bối cảnh và lịch sử hội thoại trước đó, hãy sử dụng chúng để hiểu rõ hơn về yêu cầu của người dùng và trả lời một cách phù hợp.
    Ngoài ra, bạn có thể sử dụng công cụ tìm kiếm tavily_search để tra cứu thông tin nếu cần thiết. Luôn thay đổi truy vấn tìm kiếm để có được kết quả tốt nhất, và chỉ sử dụng công cụ tavily_search khi bạn thực sự cần thông tin cập nhật hoặc chi tiết mà bạn không chắc chắn. Đảm bảo rằng câu trả lời của bạn dựa trên thông tin đã biết và tavily_search một cách cân bằng.
    Bạn có thể gọi cùng một công cụ nhiều lần nếu cần để thu thập đủ thông tin.
    Nếu có kết quả công cụ sẵn có và đã đủ để trả lời, hãy tổng hợp và trả lời.
    Nếu cần dữ liệu bổ sung, tiếp tục gọi công cụ với tham số phù hợp cho đến khi có đủ thông tin.
    """

    def __init__(
        self,
        provider: LLMProvider,
        api_key: str | None = None,
        sliding_window_size: int | None = 10,
        history: list[dict[str, Any]] | None = None,
    ):
        self.provider = provider
        self.api_key = api_key or ""
        self.conversation_history = history if history is not None else []
        # If set, keep only the most recent `sliding_window_size` messages.
        # Use None to disable trimming.
        self.sliding_window_size = sliding_window_size
        self.client = self._create_client()
        logger.info(
            "Initialized ChatService provider=%s base_url=%s history_messages=%d",
            self.provider.value,
            self.provider.base_url or "(default)",
            len(self.conversation_history),
        )

    def _create_client(self) -> OpenAI:
        """Create an OpenAI-compatible client for the selected provider."""
        if self.provider.api_key and not self.api_key:
            raise ValueError(
                f"Missing API key for provider {self.provider.value}. "
                f"Expected env var: {self.provider.api_key}"
            )

        client_api_key = self.api_key or "not-required"
        base_url = self.provider.base_url
        logger.debug(
            "Creating OpenAI-compatible client provider=%s base_url=%s api_key_configured=%s",
            self.provider.value,
            base_url or "(default)",
            bool(self.api_key),
        )
        if base_url:
            return OpenAI(api_key=client_api_key, base_url=base_url)
        return OpenAI(api_key=client_api_key)

    def _format_transcript(self, messages: list[dict[str, Any]]) -> str:
        return "\n".join(
            f"{message.get('role', 'unknown').upper()}: {message.get('content', '')}"
            for message in messages
        )

    def _turn_count(self, messages: list[dict[str, Any]]) -> int:
        return sum(1 for message in messages if message.get("role") == "user")
    def _apply_sliding_window(self) -> None:
        """Trim conversation history to the configured sliding window size.

        Keeps only the most recent `self.sliding_window_size` messages when the
        history grows beyond that size. If `self.sliding_window_size` is None,
        trimming is disabled.
        """
        if not self.sliding_window_size:
            return

        current_len = len(self.conversation_history)
        if current_len <= self.sliding_window_size:
            return

        logger.info(
            "Applying sliding window provider=%s max_messages=%d current_messages=%d",
            self.provider.value,
            self.sliding_window_size,
            current_len,
        )
        # Keep most recent messages only
        self.conversation_history = self.conversation_history[-self.sliding_window_size:]

    def _convert_response_to_dict(self, response: Any) -> dict[str, Any]:
        """Parse a non-streaming response into a chat-history message dict."""
        message_dict: dict[str, Any] = {"role": "assistant"}

        for block in getattr(response, "output", []):
            content_items = getattr(block, "content", []) or []
            text = getattr(content_items[0], "text", "") if content_items else ""

            match getattr(block, "type", None):
                case "reasoning":
                    summary = getattr(block, "summary", None) or text
                    if summary:
                        message_dict["reasoning_content"] = summary
                case "message":
                    if text:
                        message_dict["content"] = text
                case _:
                    continue

        return message_dict

    def response(
        self,
        model: str,
        input: str | dict[str, Any],
        instructions: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs,
    ):
        """Stream a response, optionally executing tools in small follow-up rounds."""
        request_id = kwargs.pop("request_id", str(uuid.uuid4()))
        request_start = time.time()
        new_message = {"role": "user", "content": input} if isinstance(input, str) else input
        self.conversation_history.append(new_message)

        logger.info(
            "[%s] Starting response provider=%s model=%s history_messages=%d input_type=%s tools_enabled=%s",
            request_id,
            self.provider.value,
            model,
            len(self.conversation_history),
            type(input).__name__,
            bool(tools if tools is not None else DEFAULT_TOOLS),
        )

        # Apply sliding window trimming to bound history size
        self._apply_sliding_window()

        effective_instructions = instructions or self.DEFAULT_INSTRUCTIONS

        request_input = self.conversation_history.copy()
        available_tools = tools if tools is not None else DEFAULT_TOOLS
        normalized_tools: list[dict[str, Any]] = []
        for tool in available_tools:
            if not isinstance(tool, dict):
                continue

            normalized_tool = dict(tool)
            nested_function = normalized_tool.get("function")
            if isinstance(nested_function, dict):
                normalized_tool.setdefault("name", nested_function.get("name"))
                normalized_tool.setdefault("description", nested_function.get("description", ""))
                normalized_tool.setdefault("parameters", nested_function.get("parameters") or {})

            if normalized_tool.get("type") == "function":
                normalized_tool["parameters"] = normalized_tool.get("parameters") or {}

            normalized_tools.append(normalized_tool)

        max_tool_rounds = kwargs.pop("max_tool_rounds", 5)
        cached_tool_outputs: dict[str, str] = {}
        logger.debug(
            "[%s] Prepared request_input_messages=%d normalized_tools=%s max_tool_rounds=%d",
            request_id,
            len(request_input),
            [tool.get("name") for tool in normalized_tools],
            max_tool_rounds,
        )

        def parse_tool_arguments(raw_arguments: Any) -> dict[str, Any]:
            if raw_arguments is None:
                return {}
            if isinstance(raw_arguments, dict):
                return raw_arguments
            if isinstance(raw_arguments, str):
                try:
                    parsed = json.loads(raw_arguments)
                    return parsed if isinstance(parsed, dict) else {"_value": parsed}
                except json.JSONDecodeError:
                    return {"_raw": raw_arguments}
            return {"_value": raw_arguments}

        def run_tool(tool_name: str, tool_args: dict[str, Any]) -> str:
            logger.info("[%s] Executing tool %s args=%s", request_id, tool_name, tool_args)
            try:
                match tool_name:
                    case "tavily_search":
                        result = tavily_search(**tool_args)
                    case "get_current_date":
                        result = get_current_date()
                    case _:
                        result = {"error": f"Unknown tool: {tool_name}"}
            except Exception as exc:
                logger.exception("Tool execution failed: %s", tool_name)
                result = {"error": str(exc), "tool": tool_name}

            if isinstance(result, str):
                logger.debug("[%s] Tool %s returned string output len=%d", request_id, tool_name, len(result))
                return result

            try:
                serialized_result = json.dumps(result, ensure_ascii=False)
                logger.debug(
                    "[%s] Tool %s returned JSON-serializable output len=%d",
                    request_id,
                    tool_name,
                    len(serialized_result),
                )
                return serialized_result
            except TypeError:
                return str(result)

        def make_tool_signature(tool_name: str, tool_args: dict[str, Any]) -> str:
            try:
                serialized_args = json.dumps(tool_args, ensure_ascii=False, sort_keys=True)
            except TypeError:
                serialized_args = repr(tool_args)
            return f"{tool_name}:{serialized_args}"

        def final_answer_stream():
            final_instructions = (
                f"{effective_instructions}\n\n"
                "Đã có kết quả từ công cụ. KHÔNG gọi công cụ nữa. "
                "Hãy tổng hợp các kết quả công cụ đã có và trả lời câu hỏi người dùng một cách rõ ràng, ngắn gọn, đúng trọng tâm."
            )
            logger.info("[%s] Running final synthesis pass with tools disabled", request_id)
            return self.client.responses.create(
                model=model,
                instructions=final_instructions,
                input=request_input,
                tools=[],
                stream=True,
                **kwargs,
            )

        try:
            for round_index in range(max_tool_rounds):
                logger.info(
                    "[%s] Starting tool round %d/%d input_messages=%d",
                    request_id,
                    round_index + 1,
                    max_tool_rounds,
                    len(request_input),
                )
                stream = self.client.responses.create(
                    model=model,
                    instructions=effective_instructions,
                    input=request_input,
                    tools=normalized_tools,
                    stream=True,
                    **kwargs,
                )

                assistant_output_text = ""
                detected_tool_calls: list[dict[str, Any]] = []

                for event in stream:
                    yield event

                    event_type = getattr(event, "type", None)
                    if event_type == OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DELTA:
                        assistant_output_text += getattr(event, "delta", "")
                    elif event_type == OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DONE:
                        done_text = getattr(event, "text", "")
                        if done_text:
                            assistant_output_text = done_text
                    elif event_type == OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_ITEM_DONE:
                        item = getattr(event, "item", None) or getattr(event, "output_item", None)
                        if not item:
                            continue

                        item_type = getattr(item, "type", None)
                        if item_type not in ("function_call", "tool_call"):
                            continue

                        tool_name = (
                            getattr(item, "name", None)
                            or getattr(item, "tool_name", None)
                            or getattr(item, "function_name", None)
                        )
                        if not tool_name:
                            continue

                        logger.info("[%s] Detected tool call name=%s", request_id, tool_name.strip())
                        detected_tool_calls.append(
                            {
                                "call_id": getattr(item, "call_id", None) or getattr(item, "id", None),
                                "name": tool_name.strip(),
                                "arguments": getattr(item, "arguments", None)
                                or getattr(item, "input", None)
                                or getattr(item, "tool_input", None),
                            }
                        )

                if not detected_tool_calls:
                    logger.info("[%s] No tool calls detected; streaming response completed", request_id)
                    return

                if assistant_output_text:
                    request_input.append({"role": "assistant", "content": assistant_output_text})
                    logger.debug(
                        "[%s] Appended assistant partial content len=%d",
                        request_id,
                        len(assistant_output_text),
                    )

                new_tool_execution = False
                for tool_call in detected_tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = parse_tool_arguments(tool_call.get("arguments"))
                    signature = make_tool_signature(tool_name, tool_args)
                    call_id = tool_call.get("call_id")

                    if not call_id:
                        logger.warning("[%s] Skip tool output append because call_id is missing for %s", request_id, tool_name)
                        continue

                    if signature in cached_tool_outputs:
                        tool_output = cached_tool_outputs[signature]
                        logger.info("[%s] Reusing cached tool output for %s", request_id, tool_name)
                    else:
                        tool_output = run_tool(tool_name, tool_args)
                        cached_tool_outputs[signature] = tool_output
                        new_tool_execution = True

                    request_input.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": str(tool_output),
                        }
                    )
                    logger.debug("[%s] Appended function_call_output for %s", request_id, tool_name)
                    # Emit a streaming event so the UI can update any
                    # placeholders with the actual tool output in real-time.
                    try:
                        yield SimpleNamespace(
                            type=OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_ITEM_DONE,
                            item=SimpleNamespace(type="function_call_output", call_id=call_id, output=str(tool_output), name=tool_name),
                        )
                    except Exception:
                        # If yielding the synthetic event fails for any reason,
                        # continue without blocking the flow. The final synthesis
                        # will still include the tool results in the model input.
                        logger.debug("[%s] Failed to yield function_call_output event for %s", request_id, call_id)

                if new_tool_execution:
                    logger.info("[%s] Completed tool round with new executions; continuing follow-up round", request_id)
                    continue

                logger.info("[%s] No new tool execution in this round; switching to final synthesis", request_id)
                for event in final_answer_stream():
                    yield event
                return

            aggregated_outputs = "\n\n".join(
                f"--- {signature.split(':', 1)[0]} ---\n{output}"
                for signature, output in cached_tool_outputs.items()
            ) or "(Không có kết quả công cụ)"
            fallback_text = (
                "Xin lỗi — quá trình tự động gọi công cụ đã vượt quá giới hạn cho phép.\n"
                "Dưới đây là kết quả tóm tắt từ các công cụ đã chạy:\n\n"
                f"{aggregated_outputs}"
            )
            logger.warning("[%s] Reached max tool rounds; returning fallback response", request_id)
            yield SimpleNamespace(
                type=OpenAIResponseAPIStreamingState.RESPONSE_OUTPUT_TEXT_DONE,
                text=fallback_text,
            )
            yield SimpleNamespace(type=OpenAIResponseAPIStreamingState.RESPONSE_COMPLETED)
        except Exception as exc:
            logger.exception(
                "[%s] Failed to generate response with provider %s and model %s",
                request_id,
                self.provider.value,
                model,
            )
            raise RuntimeError(f"Failed to generate response: {exc}") from exc
        finally:
            duration = time.time() - request_start
            logger.info(
                "[%s] Response finished provider=%s model=%s duration=%.3fs tool_cache_entries=%d final_history_messages=%d",
                request_id,
                self.provider.value,
                model,
                duration,
                len(cached_tool_outputs),
                len(self.conversation_history),
            )
