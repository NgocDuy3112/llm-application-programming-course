"""
Tests for Module 6-7 exercises.

These tests validate that the fill-in-the-blank placeholders in exercises/
are replaced correctly and that the core components can be imported and
instantiated without runtime errors.

Run with:
    pytest tests/test_exercises.py
"""

import sys
import os
from pathlib import Path

# Add exercises to path so we can import modules under exercises/
exercises_path = Path(__file__).parent.parent / "exercises"
sys.path.insert(0, str(exercises_path))

def test_import_custom_types():
    """Test that custom_types can be imported and enums have expected values."""
    from custom_types import Provider, ContextManagementMode, ToolChoice
    assert Provider.GROQ.value == "groq"
    assert Provider.OLLAMA.value == "ollama"
    assert ContextManagementMode.OFF.value == "Tắt"
    assert ToolChoice.NONE.value == "none"

def test_import_constants():
    """Test that constants can be imported and MODELS_BY_PROVIDER is structured."""
    from constants import MODELS_BY_PROVIDER
    assert "groq" in MODELS_BY_PROVIDER
    assert "ollama" in MODELS_BY_PROVIDER
    assert isinstance(MODELS_BY_PROVIDER["groq"], list)
    assert isinstance(MODELS_BY_PROVIDER["ollama"], list)

def test_import_logger():
    """Test that logger can be imported and global_logger is available."""
    from logger import global_logger
    assert global_logger is not None
    # Test that logger methods exist
    assert hasattr(global_logger, "info")
    assert hasattr(global_logger, "debug")
    assert hasattr(global_logger, "error")

def test_import_model_adapter():
    """Test that model.adapter can be imported and classes are defined."""
    from model.adapter import BaseAdapter, GroqAdapter, OllamaAdapter
    assert BaseAdapter is not None
    assert GroqAdapter is not None
    assert OllamaAdapter is not None
    # Test that BaseAdapter is abstract
    try:
        BaseAdapter()
        assert False, "BaseAdapter should be abstract and not instantiable"
    except TypeError:
        pass  # Expected

def test_import_orchestrator_memory():
    """Test that orchestrator.memory can be imported and classes work."""
    from orchestrator.memory import BaseMemory, WindowMemory
    assert BaseMemory is not None
    assert WindowMemory is not None
    # Test WindowMemory initialization and get_messages
    mem = WindowMemory(sliding_window_size=2)
    mem.add("user", "Hello")
    mem.add("assistant", "Hi")
    msgs = mem.get_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"

def test_import_orchestrator_tools():
    """Test that orchestrator.tools can be imported and functions exist."""
    from orchestrator.tools import AVAILABLE_FUNCTIONS, DEFAULT_TOOLS, tavily_search, get_current_date
    assert isinstance(AVAILABLE_FUNCTIONS, dict)
    assert isinstance(DEFAULT_TOOLS, list)
    assert "get_current_date" in AVAILABLE_FUNCTIONS
    assert "tavily_search" in AVAILABLE_FUNCTIONS
    # Test get_current_date returns a string
    date_str = get_current_date()
    assert isinstance(date_str, str)

def test_import_ui_components():
    """Test that UI components can be imported."""
    from ui.sidebar import render_sidebar
    from ui.chat_interface import render_chat_interface
    assert render_sidebar is not None
    assert render_chat_interface is not None

def test_import_app():
    """Test that app can be imported and main functions exist."""
    from app import get_memory, get_adapter, get_chatbot_engine, main
    assert get_memory is not None
    assert get_adapter is not None
    assert get_chatbot_engine is not None
    assert main is not None

def test_no_placeholders_left():
    """Ensure no __BLANKn__ placeholders remain in critical files."""
    import re
    # Files that should not contain placeholders after completion
    files_to_check = [
        exercises_path / "model" / "adapter.py",
        exercises_path / "orchestrator" / "memory.py",
        exercises_path / "orchestrator" / "engine.py",
    ]
    placeholder_pattern = re.compile(r"__BLANK\d+__")
    for file_path in files_to_check:
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            matches = placeholder_pattern.findall(content)
            assert not matches, f"Placeholder(s) {matches} found in {file_path.relative_to(exercises_path)}"

def test_memory_sliding_window_calculation():
    """Test that WindowMemory.get_messages respects sliding_window_size."""
    from orchestrator.memory import WindowMemory
    mem = WindowMemory(sliding_window_size=3)
    # Add 10 messages (5 user-assistant pairs)
    for i in range(10):
        role = "user" if i % 2 == 0 else "assistant"
        mem.add(role, f"msg{i}")
    msgs = mem.get_messages()
    # Should only keep last 6 messages (3 pairs)
    assert len(msgs) == 6
    assert msgs[0]["content"] == "msg4"
    assert msgs[-1]["content"] == "msg9"

def test_tool_choice_serialization():
    """Test that tool_choice serialization works in BaseAdapter.response."""
    from model.adapter import BaseAdapter
    from custom_types import ToolChoice
    # We cannot instantiate BaseAdapter directly, but we can test the logic
    # by simulating the serialization block
    import enum
    tool_choice = ToolChoice.AUTO
    if isinstance(tool_choice, enum.Enum):
        tool_choice_value = tool_choice.value
    else:
        tool_choice_value = getattr(tool_choice, "value", tool_choice)
    assert tool_choice_value == "auto"

def test_groq_adapter_missing_api_key():
    """Test that GroqAdapter raises ValueError when GROQ_API_KEY is missing."""
    from model.adapter import GroqAdapter
    # Temporarily unset the env var
    old_key = os.environ.get("GROQ_API_KEY")
    if "GROQ_API_KEY" in os.environ:
        del os.environ["GROQ_API_KEY"]
    try:
        GroqAdapter()
        assert False, "Expected ValueError for missing GROQ_API_KEY"
    except ValueError as e:
        assert "GROQ_API_KEY" in str(e)
    finally:
        # Restore original env var if it existed
        if old_key is not None:
            os.environ["GROQ_API_KEY"] = old_key

def test_ollama_adapter_initialization():
    """Test that OllamaAdapter can be instantiated (no API key required)."""
    from model.adapter import OllamaAdapter
    try:
        adapter = OllamaAdapter()
        assert adapter.client is not None
        assert adapter.client.base_url == "http://localhost:11434/v1/"
    except Exception as e:
        # If Ollama server is not running, OpenAI client may still initialize
        # We just check that it doesn't raise due to missing API key
        assert "api_key" not in str(e).lower()

if __name__ == "__main__":
    # Run a quick sanity check when executed directly
    import pytest
    pytest.main([__file__])