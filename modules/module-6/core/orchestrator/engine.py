import json

from orchestrator.memory import WindowMemory
from orchestrator.tools import *
from model.adapter import BaseAdapter


class ChatbotEngine:
    def __init__(self, provider: str, api_key: str | None, memory_size=5):
        self.memory = WindowMemory(k=memory_size)
        self.adapter = BaseAdapter(provider=provider, api_key=api_key)

    def response(self, model: str, input: str, instruction: str | None = None, **kwargs):
        system_message = {"role": "system", "content": instruction if instruction else "You are a helpful assistant."}
        self.memory.add(role="user", content=input)
        
        while True:
            messages = [system_message] + self.memory.get_messages()
            response = self.adapter.response(model=model, messages=messages, tools=DEFAULT_TOOLS, **kwargs)
            last_message = response.choices[0].message
            
            if not last_message.tool_calls:
                self.memory.add(role="assistant", content=last_message.content)
                return last_message.content

            self.memory.add(role="assistant", content=last_message.content, tool_calls=last_message.tool_calls)
            
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except:
                    tool_args = {}

                if tool_name in AVAILABLE_FUNCTIONS:
                    try:
                        tool_response = AVAILABLE_FUNCTIONS[tool_name](**tool_args)
                    except Exception as e:
                        tool_response = f"Error executing {tool_name}: {str(e)}"
                else:
                    tool_response = f"Unknown tool: {tool_name}"
                self.memory.add_tool_message(tool_call, tool_response)