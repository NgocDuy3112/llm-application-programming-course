from enum import Enum



class OpenAIResponseAPIStreamingState(str, Enum):
    RESPONSE_CREATED = "response.created"
    RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
    RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
    RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    RESPONSE_REASONING_TEXT_DELTA = "response.reasoning_text.delta"
    RESPONSE_REASONING_SUMMARY_TEXT_DELTA = "response.reasoning_summary_text.delta"
    RESPONSE_REASONING_TEXT_DONE = "response.reasoning_text.done"
    RESPONSE_REASONING_SUMMARY_TEXT_DONE = "response.reasoning_summary_text.done"
    RESPONSE_COMPLETED = "response.completed"