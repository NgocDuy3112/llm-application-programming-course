from enum import Enum


class Provider(Enum):
    GROQ = 'groq'
    OLLAMA = 'ollama'


class ContextManagementMode(Enum):
    OFF = "Tắt"
    SLIDING_WINDOW = "Cửa sổ trượt (sliding window)"
    RELEVANCE_FILTERING = "Tóm tắt (summarization)"


class ToolChoice(Enum):
    NONE = "none"
    AUTO = "auto"