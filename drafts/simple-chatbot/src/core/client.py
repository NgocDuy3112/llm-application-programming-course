from openai import OpenAI
from ..utils.helpers import map_dict_to_pydantic, define_api_base_url



class LLMClient:
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

    def create_response(self, input, stream: bool=True, **kwargs):
        response = self.client.responses.create(
            model=self.model, 
            stream=stream, 
            input=input,
            **kwargs)
        return response.output_text

    def create_structured_response(self, input, schema: dict, **kwargs):
        pydantic_model = map_dict_to_pydantic(schema)
        response = self.client.responses.parse(
            model=self.model,
            text_format=pydantic_model,
            input=input,
            **kwargs
        )
        return response.output_parsed