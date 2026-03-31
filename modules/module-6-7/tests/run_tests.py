#!/usr/bin/env python3
"""
Simple test runner for Module 6-7 exercises when pytest is not available.
"""

import sys
import os
import traceback
from pathlib import Path

# Add exercises and exercises/demos to Python path
exercises_path = Path(__file__).parent.parent / "exercises"
demos_exercises_path = exercises_path / "demos"
sys.path.insert(0, str(exercises_path))
sys.path.insert(0, str(demos_exercises_path))

def run_test(test_func, test_name):
    """Run a single test function and report results."""
    try:
        test_func()
        print(f"✓ {test_name}")
        return True
    except Exception as e:
        print(f"✗ {test_name}")
        print(f"  ERROR: {e}")
        traceback.print_exc()
        return False

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
    assert hasattr(global_logger, "info")
    assert hasattr(global_logger, "debug")
    assert hasattr(global_logger, "error")

def test_import_model_adapter():
    """Test that model.adapter can be imported and classes are defined."""
    from model.adapter import BaseAdapter, GroqAdapter, OllamaAdapter
    assert BaseAdapter is not None
    assert GroqAdapter is not None
    assert OllamaAdapter is not None

def test_import_orchestrator_memory():
    """Test that orchestrator.memory can be imported and classes work."""
    from orchestrator.memory import WindowMemory
    assert WindowMemory is not None
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

def test_memory_sliding_window_calculation():
    """Test that WindowMemory.get_messages respects sliding_window_size."""
    from orchestrator.memory import WindowMemory
    mem = WindowMemory(sliding_window_size=3)
    for i in range(10):
        role = "user" if i % 2 == 0 else "assistant"
        mem.add(role, f"msg{i}")
    msgs = mem.get_messages()
    assert len(msgs) == 6
    assert msgs[0]["content"] == "msg4"
    assert msgs[-1]["content"] == "msg9"

def test_placeholders_exist_in_adapter():
    """Test that __BLANKn__ placeholders exist in exercises/model/adapter.py."""
    adapter_file = exercises_path / "model" / "adapter.py"
    assert adapter_file.exists(), f"{adapter_file} does not exist"
    content = adapter_file.read_text(encoding="utf-8")
    # Check that no placeholders exist in the final version
    placeholders = ["__BLANK1__", "__BLANK2__", "__BLANK3__", "__BLANK4__", "__BLANK5__", "__BLANK6__", "__BLANK7__"]
    for ph in placeholders:
        assert ph not in content, f"Placeholder {ph} found in {adapter_file} - should be filled in"

def test_placeholders_exist_in_memory():
    """Test that __BLANKn__ placeholders exist in exercises/orchestrator/memory.py."""
    memory_file = exercises_path / "orchestrator" / "memory.py"
    assert memory_file.exists(), f"{memory_file} does not exist"
    content = memory_file.read_text(encoding="utf-8")
    assert "__BLANK8__" not in content, f"Placeholder __BLANK8__ found in {memory_file} - should be filled in"

def test_placeholders_exist_in_engine():
    """Test that __BLANKn__ placeholders exist in exercises/orchestrator/engine.py."""
    engine_file = exercises_path / "orchestrator" / "engine.py"
    assert engine_file.exists(), f"{engine_file} does not exist"
    content = engine_file.read_text(encoding="utf-8")
    placeholders = ["__BLANK9__", "__BLANK10__", "__BLANK11__", "__BLANK12__", "__BLANK13__", "__BLANK14__"]
    for ph in placeholders:
        assert ph not in content, f"Placeholder {ph} found in {engine_file} - should be filled in"

def main():
    """Run all tests and report results."""
    print("Running Module 6-7 exercise tests...")
    print("=" * 50)
    
    tests = [
        (test_import_custom_types, "Import custom_types"),
        (test_import_constants, "Import constants"),
        (test_import_logger, "Import logger"),
        (test_import_model_adapter, "Import model.adapter"),
        (test_import_orchestrator_memory, "Import orchestrator.memory"),
        (test_import_orchestrator_tools, "Import orchestrator.tools"),
        (test_import_ui_components, "Import UI components"),
        (test_import_app, "Import app"),
        (test_memory_sliding_window_calculation, "WindowMemory sliding window"),
        (test_placeholders_exist_in_adapter, "No placeholders in adapter.py"),
        (test_placeholders_exist_in_memory, "No placeholders in memory.py"),
        (test_placeholders_exist_in_engine, "No placeholders in engine.py"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, test_name in tests:
        if run_test(test_func, test_name):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed. ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())