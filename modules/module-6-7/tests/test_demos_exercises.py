"""
Tests for Module 6-7 exercises in exercises/demos/.

These tests validate that the fill-in-the-blank placeholders in exercises/demos/
are present and can be replaced correctly.

Run with:
    pytest tests/test_demos_exercises.py
"""

import sys
import os
from pathlib import Path

# Add exercises/demos to path so we can import modules under exercises/demos/
demos_exercises_path = Path(__file__).parent.parent / "exercises" / "demos"
sys.path.insert(0, str(demos_exercises_path))

def test_placeholders_exist_in_adapter():
    """Test that __BLANKn__ placeholders exist in exercises/demos/model/adapter.py."""
    adapter_file = demos_exercises_path / "model" / "adapter.py"
    assert adapter_file.exists(), f"{adapter_file} does not exist"
    content = adapter_file.read_text(encoding="utf-8")
    # Check for expected placeholders
    expected_placeholders = ["__BLANK1__", "__BLANK2__", "__BLANK3__", "__BLANK4__", "__BLANK5__", "__BLANK6__", "__BLANK7__"]
    for ph in expected_placeholders:
        assert ph in content, f"Placeholder {ph} not found in {adapter_file}"

def test_placeholders_exist_in_memory():
    """Test that __BLANKn__ placeholders exist in exercises/demos/orchestrator/memory.py."""
    memory_file = demos_exercises_path / "orchestrator" / "memory.py"
    assert memory_file.exists(), f"{memory_file} does not exist"
    content = memory_file.read_text(encoding="utf-8")
    assert "__BLANK8__" in content, f"Placeholder __BLANK8__ not found in {memory_file}"

def test_placeholders_exist_in_engine():
    """Test that __BLANKn__ placeholders exist in exercises/demos/orchestrator/engine.py."""
    engine_file = demos_exercises_path / "orchestrator" / "engine.py"
    assert engine_file.exists(), f"{engine_file} does not exist"
    content = engine_file.read_text(encoding="utf-8")
    expected_placeholders = ["__BLANK9__", "__BLANK10__", "__BLANK11__", "__BLANK12__", "__BLANK13__", "__BLANK14__"]
    for ph in expected_placeholders:
        assert ph in content, f"Placeholder {ph} not found in {engine_file}"

def test_import_custom_types_demos():
    """Test that custom_types can be imported from exercises/demos."""
    from custom_types import Provider, ContextManagementMode, ToolChoice
    assert Provider.GROQ.value == "groq"
    assert Provider.OLLAMA.value == "ollama"
    assert ContextManagementMode.OFF.value == "Tắt"
    assert ToolChoice.NONE.value == "none"

def test_import_constants_demos():
    """Test that constants can be imported from exercises/demos."""
    from constants import MODELS_BY_PROVIDER
    assert "groq" in MODELS_BY_PROVIDER
    assert "ollama" in MODELS_BY_PROVIDER
    assert isinstance(MODELS_BY_PROVIDER["groq"], list)
    assert isinstance(MODELS_BY_PROVIDER["ollama"], list)

def test_import_logger_demos():
    """Test that logger can be imported from exercises/demos."""
    from logger import global_logger
    assert global_logger is not None
    assert hasattr(global_logger, "info")
    assert hasattr(global_logger, "debug")
    assert hasattr(global_logger, "error")

def test_import_model_adapter_demos():
    """Test that model.adapter can be imported from exercises/demos."""
    from model.adapter import BaseAdapter, GroqAdapter, OllamaAdapter
    assert BaseAdapter is not None
    assert GroqAdapter is not None
    assert OllamaAdapter is not None

def test_import_orchestrator_memory_demos():
    """Test that orchestrator.memory can be imported from exercises/demos."""
    from orchestrator.memory import BaseMemory, WindowMemory
    assert BaseMemory is not None
    assert WindowMemory is not None

def test_import_orchestrator_tools_demos():
    """Test that orchestrator.tools can be imported from exercises/demos."""
    from orchestrator.tools import AVAILABLE_FUNCTIONS, DEFAULT_TOOLS, tavily_search, get_current_date
    assert isinstance(AVAILABLE_FUNCTIONS, dict)
    assert isinstance(DEFAULT_TOOLS, list)
    assert "get_current_date" in AVAILABLE_FUNCTIONS
    assert "tavily_search" in AVAILABLE_FUNCTIONS

def test_import_ui_components_demos():
    """Test that UI components can be imported from exercises/demos."""
    from ui.sidebar import render_sidebar
    from ui.chat_interface import render_chat_interface
    assert render_sidebar is not None
    assert render_chat_interface is not None

def test_import_app_demos():
    """Test that app can be imported from exercises/demos."""
    from app import get_memory, get_adapter, get_chatbot_engine, main
    assert get_memory is not None
    assert get_adapter is not None
    assert get_chatbot_engine is not None
    assert main is not None

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])