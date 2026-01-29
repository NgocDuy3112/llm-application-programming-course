from openai import OpenAI
from enum import Enum

from ..utils.helpers import map_dict_to_pydantic, define_api_base_url


class StreamingState(str, Enum):
    TEXT_STREAMING_IN_PROGRESS = "response.output_text.delta"
    TEXT_STREAMING_DONE = "response.output_text.done"
    REASONING_IN_PROGRESS = "response.reasoning_text.delta"
    REASONING_DONE = "response.reasoning_text.done"



class OpenAIStandardClient:
    def __init__(
        self, 
        model: str, 
        model_provider: str | None = None, 
        api_key: str | None = None, 
        base_url: str | None = None
    ):
        self.base_url = base_url if base_url else define_api_base_url(model_provider)
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        self.model = model

    def create_response(self, input, stream: bool, **kwargs):
        response = self.client.responses.create(
            model=self.model, 
            stream=stream, 
            input=input,
            **kwargs
        )
        if not stream:
            return response.output_text
        else:
            for event in response:
                if event.type == StreamingState.TEXT_STREAMING_IN_PROGRESS:
                    yield {'type': 'text', 'content': event.delta}
                if event.type == StreamingState.TEXT_STREAMING_DONE:
                    break
                if event.type == StreamingState.REASONING_IN_PROGRESS:
                    yield {'type': 'reasoning', 'content': event.delta}
                if event.type == StreamingState.REASONING_DONE:
                    continue

    def create_structured_response(self, input, schema: dict, **kwargs):
        pydantic_model = map_dict_to_pydantic(schema)
        response = self.client.responses.parse(
            model=self.model,
            text_format=pydantic_model,
            input=input,
            **kwargs
        )
        return response.output_parsed



class HuggingFaceClient:
    def __init__(self, model: str):
        pass