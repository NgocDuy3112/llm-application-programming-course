from enum import Enum

class OpenAIResponseAPIStreamingState(str, Enum):
    """
    Phân loại các event trong chu trình stream dựa trên OpenAI Response API.
    """
    # TODO: Khai báo các loại event theo tài liệu OpenAI Response API (Preview):
    # 1. RESPONSE_CREATED: Khi bắt đầu nhận phản hồi
    # 2. RESPONSE_OUTPUT_TEXT_DELTA: Khi nhận được một phần text của câu trả lời
    # 3. RESPONSE_REASONING_TEXT_DELTA: Khi nhận được một phần text của suy luận (reasoning)
    # 4. RESPONSE_COMPLETED: Khi kết thúc stream
    RESPONSE_CREATED = "response.created"
    RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
    RESPONSE_REASONING_TEXT_DELTA = "response.reasoning_text.delta"
    RESPONSE_COMPLETED = "response.completed"

