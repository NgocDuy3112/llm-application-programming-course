import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


class ChatbotLogger:
    _instances = {}

    def __init__(self, name: str = "chatbot", level: int = logging.DEBUG, log_dir: str = "logs"):
        self.name = name
        self.level = level
        self.log_dir = Path(log_dir)
        self._logger: logging.Logger | None = None
        self._setup()

    def _setup(self) -> None:
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG)
        if self._logger.handlers:
            return

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)

        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.log_dir = Path('.')

        log_file = self.log_dir / f"chatbot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=5_000_000,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

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
        if name not in cls._instances:
            cls._instances[name] = cls(name=name, **kwargs)
        return cls._instances[name]._logger

    def debug(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self._logger.critical(message, *args, **kwargs)


global_logger = ChatbotLogger.get_logger()
