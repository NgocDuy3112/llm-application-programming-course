"""
Module 6-7 - Exercises Logger

Mô tả: Logger implementation cho exercises folder. Đây là bản sao từ
demos/logger.py, được cung cấp sẵn để sinh viên sử dụng trong bài tập.

Mô tả chi tiết: Triển khai logging system cho ứng dụng chatbot với:
- Console handler: Hiển thị logs từ INFO level trở lên
- File handler: Ghi logs từ DEBUG level trở lên với rotation (5MB/file)
- Singleton pattern: Đảm bảo chỉ có 1 logger instance per name

Kiến trúc / Design Patterns:
- Singleton: ChatbotLogger.get_logger() trả về cùng instance cho cùng tên
- Factory: Tạo logger với cấu hình tùy chỉnh
- Rotation: Tự động xoay log file khi đạt 5MB, giữ tối đa 5 backups

Usage:
    from exercises.logger import global_logger
    global_logger.info("User logged in")
    global_logger.error("API call failed")
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


class ChatbotLogger:
    """
    Logger class cho chatbot application với console và file handlers.

    Attributes:
        name (str): Tên logger
        level (int): Logging level cho console handler
        log_dir (Path): Thư mục chứa log files
        _logger (logging.Logger): Underlying logger instance

    Class Attributes:
        _instances (dict): Singleton registry - maps name to ChatbotLogger instance
    """

    _instances = {}

    def __init__(
        self,
        name: str = "chatbot",
        level: int = logging.DEBUG,
        log_dir: str = "logs"
    ):
        """
        Khởi tạo logger với console và file handlers.

        Args:
            name (str): Tên logger (default: "chatbot")
            level (int): Logging level cho console handler (default: DEBUG)
            log_dir (str): Thư mục chứa log files (default: "logs")
        """
        self.name = name
        self.level = level
        self.log_dir = Path(log_dir)
        self._logger: logging.Logger | None = None
        self._setup()

    def _setup(self) -> None:
        """
        Cấu hình logger với handlers và formatters.

        Setup bao gồm:
        1. Tạo logger với DEBUG level (để capture tất cả logs)
        2. Console handler: INFO+ levels, output ra stdout
        3. File handler: DEBUG+ levels, rotation 5MB/file, giữ 5 backups
        4. Formatter: timestamp - name - level - message
        """
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

        # Avoid duplicate handlers (important for singleton pattern)
        if self._logger.handlers:
            return

        # Console handler (INFO level and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)

        # Create logs directory if it doesn't exist
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback to current directory if we cannot create the logs directory
            self.log_dir = Path('.')

        # File handler with rotation (DEBUG level and above)
        # Filename format: chatbot_YYYYMMDD.log (new file each day)
        log_file = self.log_dir / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=5_000_000,  # 5MB per file
            backupCount=5,       # Keep 5 backup files
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatter: timestamp - logger name - level - message
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
        Get or create logger instance (singleton pattern).

        Args:
            name (str): Logger name (default: "chatbot")
            **kwargs: Additional arguments for logger initialization

        Returns:
            logging.Logger: Configured logger instance

        Example:
            >>> logger = ChatbotLogger.get_logger("my_module")
            >>> logger.info("Message")
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name=name, **kwargs)
        return cls._instances[name]._logger

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message - chi tiết fine-grained cho debugging."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message - sự kiện bình thường trong hoạt động."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message - vấn đề tiềm ẩn cần lưu ý."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message - lỗi nghiêm trọng cần xử lý."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message - lỗi rất nghiêm trọng, ứng dụng có thể dừng."""
        self._logger.critical(message, *args, **kwargs)


# Create default global_logger instance - được import và sử dụng khắp ứng dụng
global_logger = ChatbotLogger.get_logger()
