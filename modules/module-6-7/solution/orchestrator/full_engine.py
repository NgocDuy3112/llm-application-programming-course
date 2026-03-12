import json
from logger import global_logger
from core.orchestrator.memory import WindowMemory
from core.orchestrator.tools import *
from core.model.adapter import BaseAdapter



class FullChatbotEngine:
    def __init__(self, provider: str, memory_size=5):
        global_logger.debug(f"Initializing FullChatbotEngine with provider={provider}, memory_size={memory_size}")
        self.memory = WindowMemory(k=memory_size)
        self.adapter = BaseAdapter(provider=provider)

    def response(
        self, 
        model: str, 
        input: str, 
        tools: list | None = DEFAULT_TOOLS,
        instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 65536,
        **kwargs
    ):
        global_logger.info(f"Processing user input: {input[:50]}...")
        system_message = {"role": "system", "content": instruction if instruction else "You are a helpful assistant."}
        self.memory.add(role="user", content=input)
        
        while True:
            messages = [system_message] + self.memory.get_messages()
            response = self.adapter.response(
                model=model, 
                messages=messages, 
                tools=tools, 
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
            last_message = response.choices[0].message
            
            if not last_message.tool_calls:
                global_logger.debug(f"No tool calls, returning assistant response")
                self.memory.add(role="assistant", content=last_message.content)
                return last_message.content

            global_logger.debug(f"Tool calls detected: {[tc.function.name for tc in last_message.tool_calls]}")
            self.memory.add(role="assistant", content=last_message.content, tool_calls=last_message.tool_calls)

            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                global_logger.debug(f"Executing tool: {tool_name}")
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except:
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
                self.memory.add_tool_message(tool_call, tool_response)