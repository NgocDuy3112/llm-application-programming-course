from enum import Enum


class OpenAIResponseAPIStreamingState(str, Enum):
    RESPONSE_CREATED = "response.created"
    RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
    RESPONSE_REASONING_TEXT_DELTA = "response.reasoning_text.delta"
    RESPONSE_COMPLETED = "response.completed"