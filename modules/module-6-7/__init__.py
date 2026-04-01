"""
Demos package for Module 6-7 - Building Basic Chatbots.

This package contains a complete chatbot application demo with:
- UI components (Streamlit-based)
- Model adapters (Groq, Ollama)
- Orchestrator (engine, memory, tools)
- Logging infrastructure

Subpackages:
    model: LLM adapter implementations
    orchestrator: Chat engine, memory management, tool execution
    ui: Streamlit UI components

Usage:
    from demos.app import main
    from demos.model.adapter import GroqAdapter, OllamaAdapter
    from demos.orchestrator.engine import FullChatbotEngine
"""

__all__ = [
    "app",
    "model",
    "orchestrator",
    "ui",
    "logger",
    "constants",
    "custom_types",
]
