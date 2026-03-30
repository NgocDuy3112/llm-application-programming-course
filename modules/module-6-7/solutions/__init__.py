"""
Solutions package for Module 6-7 - Building Basic Chatbots.

This package contains solution implementations for the exercises.
Students can reference these solutions to understand the expected implementation.

Modules:
    logger: Pre-configured logging infrastructure với singleton pattern
    app: Complete chatbot application với full integration
    constants: Constants for models and providers
    custom_types: Custom enum types (Provider, ContextManagementMode, ToolChoice)

Architecture:
    - model.adapter: LLM providers abstraction (Groq, Ollama)
    - orchestrator.engine: Chat processing logic với tool execution
    - orchestrator.memory: Context management (sliding window)
    - orchestrator.tools: Function calling implementations
    - ui.*: Streamlit user interface components

Usage:
    Run with: streamlit run solutions/app.py
    
See Also:
    exercises/: Exercise templates for students to implement
"""

__all__ = ["logger", "app"]
