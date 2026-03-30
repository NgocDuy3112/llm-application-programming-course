"""
Orchestrator package for Module 6-7 exercises.

Contains the core chatbot orchestration logic:
- Engine: Manages conversation flow and tool execution
- Memory: Handles chat history with different strategies
- Tools: Implements function calling capabilities

Modules:
    engine: FullChatbotEngine for conversation orchestration
    memory: BaseMemory, WindowMemory for context management
    tools: Available functions and tool definitions

Usage:
    from orchestrator.engine import FullChatbotEngine
    from orchestrator.memory import WindowMemory
    from orchestrator.tools import DEFAULT_TOOLS
"""

__all__ = ["engine", "memory", "tools"]
