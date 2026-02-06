"""Business logic for chat operations"""

import json
from typing import Any
from collections.abc import Generator

from src.core.client import OpenAIStandardClient
from src.core.exceptions import ValidationError
from logger import ChatbotLogger
from src.utils.settings import MAX_HISTORY_MESSAGES


logger = ChatbotLogger.get_logger("chat_service")


class ChatService:
    """Service for handling chat operations"""
    
    def __init__(self, client: OpenAIStandardClient):
        self.client = client

    @staticmethod
    def sliding_window(history: list[dict], max_messages: int) -> list[dict]:
        """Return the last `max_messages` messages from the history.

        This is a pure function and does not depend on Streamlit.
        """
        if not isinstance(history, list):
            return history
        if max_messages <= 0:
            return []
        if len(history) <= max_messages:
            return history
        return history[-max_messages:]

    def summarize_conversation(self, history: list[dict], instructions: str | None = None) -> list[dict]:
        """Build a summarization prompt for the model.

        The returned value is a list of messages structured as:
            - system instruction
            - the conversation messages (chronological)
            - a final user instruction requesting a concise summary (3-5 bullets)

        This function does NOT call the model; it only constructs the prompt.
        """
        if not isinstance(history, list) or len(history) == 0:
            return []

        summarization_instruction = (
            "HÃY TÓM TẮT VÀ TRẢ LỜI: Trước tiên, tóm tắt ngắn gọn các điểm chính và các hành động cần thực hiện "
            "(3-5 gạch đầu dòng). Sau đó, dựa trên tóm tắt, tiếp tục trả lời câu hỏi hoặc phản hồi của người dùng cuối cùng. "
            "Chỉ trả về phần tóm tắt và phần trả lời, không lặp lại toàn bộ hội thoại. Viết bằng tiếng Việt."
        )

        # Build prompt logic with correct message structure
        summ_prompt = []
        if instructions:
            summ_prompt.append({"role": "system", "content": instructions})
        else:
            summ_prompt.append({"role": "system", "content": summarization_instruction})
            
        summ_prompt.extend(history)

        summary_resp = self.client.create_response(
            input=summ_prompt,
            stream=False,
            max_output_tokens=256,
            temperature=0.2,
        )
        if isinstance(summary_resp, str):
            summary_text = summary_resp
        elif hasattr(summary_resp, "output_text"):
            summary_text = str(summary_resp.output_text)
        elif isinstance(summary_resp, dict) and "output_text" in summary_resp:
            summary_text = str(summary_resp["output_text"])
        else:
            summary_text = str(summary_resp)
        return summary_text


    def create_response(
        self,
        mode: str,
        input_data: list,
        instructions: str = "",
        max_output_tokens: int = 512,
        temperature: float = 0.7,
        schema: dict | None = None,
        use_sliding_window: bool = False,
        use_summarization: bool = False,
        max_history_messages: int | None = None,
    ) -> str | Generator:
        """
        Create chat response based on mode
        
        Args:
            mode: 'streaming', 'non-streaming', or 'structured'
            input_data: Chat history
            instructions: Custom instructions
            max_output_tokens: Maximum output tokens
            temperature: Temperature setting
            schema: Output schema for structured mode
            
        Returns:
            Response text or generator
        """
        kwargs = {
            "input": input_data,
            "instructions": instructions,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        # Apply chat history management techniques based on provided flags (no Streamlit here)
        if use_sliding_window and use_summarization:
            raise ValidationError("Only one context management strategy should be enabled at a time")

        try:
            if use_summarization:
                # First, call the client to summarize the full history (non-streaming).
                try:
                    summary_text = self.summarize_conversation(input_data, instructions=None)
                    kwargs["input"] = input_data + [{"role": "user", "content": summary_text}]
                except Exception as e:
                    logger.debug(f"Summarization call failed: {e}; proceeding without summarization")
                    kwargs["input"] = input_data
            elif use_sliding_window:
                n = max_history_messages or MAX_HISTORY_MESSAGES
                input_data = self.sliding_window(input_data, n)
                kwargs["input"] = input_data
            else:
                kwargs["input"] = input_data
        except Exception:
            # If anything goes wrong, fall back to original input_data
            kwargs["input"] = input_data
        if mode == "structured":
            if not schema:
                raise ValidationError("Schema không được để trống cho chế độ structured")
            self.validate_schema(schema)
            kwargs["schema"] = schema
            kwargs["stream"] = False
            response = self.client.create_structured_response(**kwargs)
            
            # Convert Pydantic model to dict
            if hasattr(response, "model_dump"):
                data = response.model_dump()
            elif hasattr(response, "dict"):
                data = response.dict()
            else:
                data = response
            
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        elif mode == "streaming":
            kwargs["stream"] = True
            return self.client.create_response(**kwargs)
        
        else:  # non-streaming
            kwargs["stream"] = False
            return self.client.create_response(**kwargs)
    
    @staticmethod
    def validate_input(user_input: str) -> None:
        """Validate user input"""
        if not user_input or not user_input.strip():
            raise ValidationError("Tin nhắn không được để trống")
        
        if len(user_input) > 10000:
            raise ValidationError("Tin nhắn quá dài (tối đa 10000 ký tự)")
    
    @staticmethod
    def validate_schema(schema: dict) -> None:
        """Validate output schema"""
        if not schema:
            raise ValidationError("Schema không được để trống")
        
        valid_types = {'str', 'int', 'float', 'bool'}
        for field_name, field_info in schema.items():
            if isinstance(field_info, dict):
                field_type = field_info.get('type', 'str')
            else:
                field_type = str(field_info)
            
            if field_type not in valid_types:
                raise ValidationError(
                    f"Type '{field_type}' không hợp lệ cho field '{field_name}'"
                )