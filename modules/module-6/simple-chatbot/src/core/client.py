from openai import OpenAI
from enum import Enum

import logger

from ..utils.helpers import map_dict_to_pydantic, define_api_base_url
from .exceptions import handle_api_errors, retry_on_error, ValidationError
from logger import ChatbotLogger

# Initialize logger
logger = ChatbotLogger.get_logger("client")



class OpenAIStreamingState(str, Enum):
    TEXT_STREAMING_IN_PROGRESS = "response.output_text.delta"
    TEXT_STREAMING_DONE = "response.output_text.done"
    REASONING_IN_PROGRESS = "response.reasoning_text.delta"
    REASONING_DONE = "response.reasoning_text.done"
    RESPONSE_COMPLETED = "response.completed"



class OpenAIStandardClient:
    def __init__(
        self, 
        model: str, 
        model_provider: str | None = None, 
        api_key: str | None = None, 
        base_url: str | None = None
    ):
        self.base_url = base_url if base_url else define_api_base_url(model_provider)
        self.api_key = api_key if api_key else "api-key-not-provided"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = model

    @retry_on_error(max_retries=2, delay=1.0, logger=logger)
    @handle_api_errors(logger=logger, reraise=True)
    def create_response(self, input, stream: bool, **kwargs):
        
        if not input or (isinstance(input, str) and not input.strip()):
            logger.error("Empty input provided")
            raise ValidationError("Input không được để trống")
        
        logger.info(f"Creating response for model: {self.model}, stream: {stream}")
        
        response = self.client.responses.create(
            model=self.model, 
            stream=stream, 
            input=input,
            **kwargs
        )
        
        if not stream:
            logger.debug("Non-streaming response completed")
            return response.output_text
        else:
            logger.debug("Starting streaming response")
            for event in response:
                if event.type == OpenAIStreamingState.TEXT_STREAMING_IN_PROGRESS:
                    yield {'type': 'text', 'content': event.delta}
                if event.type == OpenAIStreamingState.TEXT_STREAMING_DONE:
                    logger.debug("Streaming completed")
                if event.type == OpenAIStreamingState.REASONING_IN_PROGRESS:
                    yield {'type': 'reasoning', 'content': event.delta}
                if event.type == OpenAIStreamingState.REASONING_DONE:
                    continue
                if event.type == OpenAIStreamingState.RESPONSE_COMPLETED:
                    # TODO #1: Add a way to log token usage for streaming responses
                    # Write your code here

    @retry_on_error(max_retries=2, delay=1.0, logger=logger)
    @handle_api_errors(logger=logger, reraise=True)
    def create_structured_response(self, input, schema: dict, **kwargs):
        if not input or (isinstance(input, str) and not input.strip()):
            logger.error("Empty input provided")
            raise ValidationError("Input không được để trống")
        
        if not schema:
            logger.error("Empty schema provided")
            raise ValidationError("Schema không được để trống")
        
        logger.info(f"Creating structured response with schema: {list(schema.keys())}")
        
        # TODO #4: Parse structured response using Pydantic model
        try:
            pydantic_model = map_dict_to_pydantic(schema)
        except Exception as e:
            logger.error(f"Failed to create Pydantic model from schema: {e}")
            raise ValidationError(f"Schema không hợp lệ: {e}") from e
        
        ## Write your code here
        
        logger.debug("Structured response parsed successfully")
        return response.output_parsed