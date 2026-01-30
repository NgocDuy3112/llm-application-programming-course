import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


class ChatbotLogger:
    """Logger class for chatbot application with console and file handlers"""
    
    _instances = {}
    
    def __init__(
        self, 
        name: str = "chatbot",
        level: int = logging.INFO,
        log_dir: str = "logs"
    ):
        """
        Initialize logger with console and file handlers
        
        Args:
            name: Logger name
            level: Logging level for console
            log_dir: Directory to store log files
        """
        self.name = name
        self.level = level
        self.log_dir = Path(log_dir)
        self._logger: logging.Logger | None = None
        self._setup()
    
    def _setup(self) -> None:
        """Setup logger with handlers and formatters"""
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.level)
        # Avoid duplicate handlers
        if self._logger.handlers:
            return
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        # File handler with rotation
        log_file = self.log_dir / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)
    
    @classmethod
    def get_logger(cls, name: str = "chatbot", **kwargs) -> logging.Logger:
        """
        Get or create logger instance (singleton pattern)
        
        Args:
            name: Logger name
            **kwargs: Additional arguments for logger initialization
            
        Returns:
            Logger instance
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name=name, **kwargs)
        return cls._instances[name]._logger
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message"""
        self._logger.critical(message, *args, **kwargs)


# Create default logger instance
logger = ChatbotLogger.get_logger()