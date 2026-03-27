"""
Orchestrator package for Module 6-7 demos.

Contains the core chatbot orchestration logic:
- Engine: Manages conversation flow and tool execution
- Memory: Handles chat history with different strategies
- Tools: Implements function calling capabilities

Modules:
    engine: FullChatbotEngine for conversation orchestration
    memory: BaseMemory, WindowMemory for context management
    tools: Available functions and tool definitions

Usage:
    from demos.orchestrator.engine import FullChatbotEngine
    from demos.orchestrator.memory import WindowMemory
    from demos.orchestrator.tools import DEFAULT_TOOLS
"""

__all__ = ["engine", "memory", "tools"]
