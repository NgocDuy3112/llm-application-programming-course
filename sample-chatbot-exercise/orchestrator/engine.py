import json

from logger import global_logger
from orchestrator.tools import *
from orchestrator.memory import *
from model.adapter import *


class FullChatbotEngine:
    def __init__(self, adapter: BaseAdapter, memory: SlidingWindowMemory):
        global_logger.debug(f"Initializing ChatbotEngine with adapter={adapter.__class__.__name__}")
        self.adapter = adapter
        self.memory = memory

    def response(
        self,
        model: str,
        user_prompt: str,
        system_prompt: str | None = None,
        tools: list | None = None,
        tool_choice: ToolChoice = ToolChoice.NONE,
        temperature: float = 0.2,
        max_tokens: int = 65536,
        **kwargs
    ) -> str:
        global_logger.info(f"Processing user input: {user_prompt[:50]}...")
        system_message = {"role": "system", "content": system_prompt if system_prompt else ""}
        tools = tools if tool_choice != ToolChoice.NONE else None
        user_message = {"role": "user", "content": user_prompt}
        if self.memory is not None:
            self.memory.add(user_message)
        if system_prompt:
            messages = [system_message] + (self.memory.get_messages() if self.memory is not None else [user_message])
        else:
            messages = self.memory.get_messages() if self.memory is not None else [user_message]

        while True:
            response = self.adapter.response(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            last_message = response.choices[0].message

            if not last_message.tool_calls:
                global_logger.debug("No tool calls, returning assistant response")
                assistant_message = {"role": "assistant", "content": last_message.content}
                if self.memory is not None:
                    self.memory.add(assistant_message)
                return last_message.content

            global_logger.debug(f"Tool calls detected: {[tc.function.name for tc in last_message.tool_calls]}")
            messages.append({
                "role": "assistant",
                "content": last_message.content,
                "tool_calls": last_message.tool_calls
            })

            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                global_logger.debug(f"Executing tool: {tool_name}")
                try:
                    tool_args = json.loads(tool_call.function.arguments) or {}
                except Exception:
                    tool_args = {}

                if tool_name in AVAILABLE_FUNCTIONS:
                    try:
                        global_logger.debug(f"Calling {tool_name} with args: {tool_args}")
                        tool_response = AVAILABLE_FUNCTIONS[tool_name](**tool_args)
                    except Exception as e:
                        global_logger.error(f"Error executing {tool_name}: {str(e)}")
                        tool_response = f"Error executing {tool_name}: {str(e)}"
                else:
                    global_logger.warning(f"Unknown tool: {tool_name}")
                    tool_response = f"Unknown tool: {tool_name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(tool_response)
                })
