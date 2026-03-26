# Import logging module để làm việc với logging system
import logging
# Import sys module để access sys.stdout cho console handler
import sys
# Import datetime từ datetime module để tạo timestamp cho log filenames
from datetime import datetime
# Import Path từ pathlib module để làm việc với file paths một cách cross-platform
from pathlib import Path
# Import RotatingFileHandler để tạo log files với rotation (xoay vòng khi đạt kích thước tối đa)
from logging.handlers import RotatingFileHandler


# Định nghĩa class ChatbotLogger - custom logger wrapper cho ứng dụng chatbot
class ChatbotLogger:
    """
    Logger class cho chatbot application với console và file handlers.

    Features:
        - Singleton pattern: chỉ tạo 1 instance per logger name
        - Console handler: output ra stdout cho các messages từ INFO trở lên
        - File handler: lưu vào file với rotation cho tất cả messages từ DEBUG trở lên
        - Thread-safe: sử dụng class-level dictionary để quản lý instances

    Attributes:
        _instances (dict): Class-level dictionary lưu trữ các logger instances (singleton)
    """

    # Class-level dictionary để lưu trữ các logger instances (singleton pattern)
    # Key: logger name, Value: ChatbotLogger instance
    _instances = {}

    # Constructor của ChatbotLogger class
    def __init__(
        self,
        name: str = "chatbot",    # Tên của logger
        level: int = logging.DEBUG,  # Logging level cho console handler
        log_dir: str = "logs"    # Directory để lưu log files
    ):
        """
        Initialize logger với console và file handlers.

        Args:
            name (str): Logger name (default: "chatbot")
            level (int): Logging level cho console handler (default: DEBUG)
            log_dir (str): Directory để lưu log files (default: "logs")
        """
        # Lưu name vào instance variable
        self.name = name
        # Lưu level vào instance variable
        self.level = level
        # Convert log_dir string thành Path object để dễ làm việc với paths
        self.log_dir = Path(log_dir)
        # Variable để lưu logger instance, sẽ được khởi tạo trong _setup()
        self._logger: logging.Logger | None = None
        
        # Gọi method _setup() để khởi tạo logger với handlers và formatters
        self._setup()

    # Private method để setup logger với handlers và formatters
    def _setup(self) -> None:
        """
        Setup logger với handlers và formatters.

        Creates:
            - Console handler (INFO level and above)
            - File handler với rotation (DEBUG level and above)
        """
        # Tạo logger object với name đã chỉ định
        # logging.getLogger() trả về logger instance từ Python logging system
        self._logger = logging.getLogger(self.name)
        
        # Set level cho logger là DEBUG để capture tất cả messages
        # Logger level phải thấp hơn hoặc bằng handler levels
        self._logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

        # Kiểm tra nếu logger đã có handlers (tránh duplicate handlers)
        # self._logger.handlers là list chứa tất cả handlers đã được add
        if self._logger.handlers:
            # Nếu đã có handlers rồi thì thoát, không tạo thêm
            return

        # ================================================================
        # CONSOLE HANDLER
        # ================================================================
        # Tạo console handler để output ra stdout
        # StreamHandler(sys.stdout) gửi log messages ra standard output
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Set level cho console handler là self.level (thường là INFO hoặc DEBUG)
        # Chỉ messages từ level này trở lên mới được hiển thị
        console_handler.setLevel(self.level)

        # ================================================================
        # FILE HANDLER
        # ================================================================
        # Tạo directory cho logs nếu chưa tồn tại
        try:
            # mkdir(parents=True) tạo tất cả parent directories nếu cần
            # exist_ok=True không raise error nếu directory đã tồn tại
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback: nếu không thể tạo directory thì dùng current directory
            # Có thể do permission issues hoặc các lỗi khác
            self.log_dir = Path('.')

        # Tạo log filename với timestamp
        # datetime.now().strftime('%Y%m%d') tạo string format YYYYMMDD
        # Ví dụ: "chatbot_20250324.log"
        log_file = self.log_dir / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Tạo rotating file handler
        # RotatingFileHandler tự động rotate log files khi đạt kích thước tối đa
        file_handler = RotatingFileHandler(
            # Đường dẫn file log (convert sang string)
            str(log_file),
            # maxBytes=5_000_000: rotation khi file đạt 5MB (5,000,000 bytes)
            maxBytes=5_000_000,  # 5MB per file
            # backupCount=5: giữ tối đa 5 backup files
            # Khi đạt 5 files, file cũ nhất sẽ bị xóa khi rotate
            backupCount=5,
            # encoding='utf-8': dùng UTF-8 encoding để hỗ trợ Unicode
            encoding='utf-8'
        )
        
        # Set level cho file handler là DEBUG để capture tất cả messages
        file_handler.setLevel(logging.DEBUG)

        # ================================================================
        # FORMATTER
        # ================================================================
        # Tạo formatter để định dạng log messages
        # Format: "YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message"
        formatter = logging.Formatter(
            # Format string với các placeholders:
            # %(asctime)s: Timestamp
            # %(name)s: Logger name
            # %(levelname)s: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            # %(message)s: Log message
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            # Date format: YYYY-MM-DD HH:MM:SS
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set formatter cho console handler
        console_handler.setFormatter(formatter)
        
        # Set formatter cho file handler
        file_handler.setFormatter(formatter)

        # Add console handler vào logger
        self._logger.addHandler(console_handler)
        
        # Add file handler vào logger
        self._logger.addHandler(file_handler)

    # Class method để get hoặc tạo logger instance (singleton pattern)
    @classmethod
    def get_logger(cls, name: str = "chatbot", **kwargs) -> logging.Logger:
        """
        Get or create logger instance (singleton pattern).

        Args:
            name (str): Logger name (default: "chatbot")
            **kwargs: Additional arguments cho logger initialization

        Returns:
            logging.Logger: Logger instance

        Example:
            >>> logger = ChatbotLogger.get_logger("my_module")
            >>> logger.info("Hello")
        """
        # Kiểm tra nếu logger name chưa có trong _instances dictionary
        if name not in cls._instances:
            # Tạo instance mới và lưu vào dictionary
            # cls(name=name, **kwargs) gọi constructor với parameters
            cls._instances[name] = cls(name=name, **kwargs)
        
        # Trả về logger object từ instance
        # cls._instances[name]._logger trả về logging.Logger object
        return cls._instances[name]._logger

    # Method để log debug messages
    def debug(self, message: str, *args, **kwargs) -> None:
        """
        Log debug message.

        Args:
            message (str): Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # Gọi logger.debug() từ Python logging system
        self._logger.debug(message, *args, **kwargs)

    # Method để log info messages
    def info(self, message: str, *args, **kwargs) -> None:
        """
        Log info message.

        Args:
            message (str): Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # Gọi logger.info() từ Python logging system
        self._logger.info(message, *args, **kwargs)

    # Method để log warning messages
    def warning(self, message: str, *args, **kwargs) -> None:
        """
        Log warning message.

        Args:
            message (str): Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # Gọi logger.warning() từ Python logging system
        self._logger.warning(message, *args, **kwargs)

    # Method để log error messages
    def error(self, message: str, *args, **kwargs) -> None:
        """
        Log error message.

        Args:
            message (str): Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # Gọi logger.error() từ Python logging system
        self._logger.error(message, *args, **kwargs)

    # Method để log critical messages
    def critical(self, message: str, *args, **kwargs) -> None:
        """
        Log critical message.

        Args:
            message (str): Log message
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # Gọi logger.critical() từ Python logging system
        self._logger.critical(message, *args, **kwargs)


# ================================================================
# GLOBAL LOGGER INSTANCE
# ================================================================
# Tạo default global_logger instance dùng singleton pattern
# Gọi get_logger() với default name "chatbot"
# Instance này có thể được import và sử dụng trong toàn bộ application
global_logger = ChatbotLogger.get_logger()
