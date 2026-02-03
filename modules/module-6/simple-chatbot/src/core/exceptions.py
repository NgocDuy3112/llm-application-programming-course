"""Custom exceptions and error handling decorators for chatbot"""

import functools
from collections.abc import Callable
from typing import Any
from openai import (
    APIError,
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
    APITimeoutError,
    BadRequestError
)


class ChatbotError(Exception):
    """Base exception for chatbot errors"""
    pass


class APIKeyError(ChatbotError):
    """Raised when API key is invalid or missing"""
    pass


class ModelError(ChatbotError):
    """Raised when model configuration is invalid"""
    pass


class ValidationError(ChatbotError):
    """Raised when input validation fails"""
    pass


class ResponseError(ChatbotError):
    """Raised when response parsing fails"""
    pass


def handle_api_errors(
    logger: Any = None,
    reraise: bool = False,
    default_return: Any = None
) -> Callable:
    """
    Decorator to handle API errors gracefully
    
    Args:
        logger: Logger instance for logging errors
        reraise: Whether to reraise the exception after handling
        default_return: Default value to return on error (if not reraising)
        
    Usage:
        @handle_api_errors(logger=logger, reraise=True)
        def create_response(self, input, **kwargs):
            ...
    """
    # TODO #3: Handle RateLimitError and provide a friendly message
    # Solution:
    # except RateLimitError as e:
    #     error_msg = f"Vượt quá giới hạn request. Vui lòng thử lại sau: {str(e)}"
    #     if logger:
    #         logger.warning(error_msg)
    #     if reraise:
    #         raise ChatbotError(error_msg) from e
    #     return default_return
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except AuthenticationError as e:
                error_msg = f"API Key không hợp lệ hoặc bị từ chối: {str(e)}"
                if logger:
                    logger.error(error_msg, exc_info=True)
                if reraise:
                    raise APIKeyError(error_msg) from e
                return default_return
            
            except RateLimitError as e:
                error_msg = f"Vượt quá giới hạn request. Vui lòng thử lại sau: {str(e)}"
                if logger:
                    logger.warning(error_msg)
                if reraise:
                    raise ChatbotError(error_msg) from e
                return default_return
            
            except APITimeoutError as e:
                error_msg = f"Request timeout. Vui lòng thử lại: {str(e)}"
                if logger:
                    logger.error(error_msg)
                if reraise:
                    raise ChatbotError(error_msg) from e
                return default_return
            
            except APIConnectionError as e:
                error_msg = f"Không thể kết nối đến API: {str(e)}"
                if logger:
                    logger.error(error_msg, exc_info=True)
                if reraise:
                    raise ChatbotError(error_msg) from e
                return default_return
            
            except BadRequestError as e:
                error_msg = f"Request không hợp lệ: {str(e)}"
                if logger:
                    logger.error(error_msg)
                if reraise:
                    raise ValidationError(error_msg) from e
                return default_return
            
            except APIError as e:
                error_msg = f"Lỗi API: {str(e)}"
                if logger:
                    logger.error(error_msg, exc_info=True)
                if reraise:
                    raise ChatbotError(error_msg) from e
                return default_return
            
            except Exception as e:
                error_msg = f"Lỗi không xác định: {str(e)}"
                if logger:
                    logger.critical(error_msg, exc_info=True)
                if reraise:
                    raise ChatbotError(error_msg) from e
                return default_return
        return wrapper
    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (APIError, APIConnectionError, APITimeoutError),
    logger: Any = None
) -> Callable:
    """
    Decorator to retry function on specific exceptions
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        logger: Logger instance
        
    Usage:
        @retry_on_error(max_retries=3, logger=logger)
        def api_call(self):
            ...
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        if logger:
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                                f"Retrying in {current_delay}s..."
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        if logger:
                            logger.error(f"All {max_retries} retry attempts failed")
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator