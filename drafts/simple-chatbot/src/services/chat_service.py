"""Business logic for chat operations"""

import json
from typing import Any, Generator
import streamlit as st

from src.core.client import OpenAIStandardClient
from src.core.exceptions import ChatbotError, APIKeyError, ValidationError
from logger import ChatbotLogger

logger = ChatbotLogger.get_logger("chat_service")


class ChatService:
    """Service for handling chat operations"""
    
    def __init__(self, client: OpenAIStandardClient):
        self.client = client
    
    def create_response(
        self,
        mode: str,
        input_data: list,
        instructions: str = "",
        max_output_tokens: int = 512,
        temperature: float = 0.7,
        schema: dict | None = None,
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
        
        if mode == "structured":
            if not schema:
                raise ValidationError("Schema không được để trống cho chế độ structured")
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