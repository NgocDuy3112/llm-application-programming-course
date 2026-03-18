import json

from logger import global_logger
from orchestrator.memory import *
from orchestrator.tools import *
from model.adapter import *
from orchestrator.safety import check_prompt_injection, check_pii, mask_pii as mask_pii_fn




class FullChatbotEngine:
    def __init__(self, adapter: BaseAdapter | None = None, memory: BaseMemory | None = None):
        """
        Khởi tạo engine với adapter và memory.
        
        Args:
            adapter: BaseAdapter instance - nếu có thì dùng cái này thay vì tạo từ provider
            memory: BaseMemory instance - nếu None thì tạo mặc định
        """
        global_logger.debug(f"Initializing FullChatbotEngine with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__}")
        self.adapter = adapter
        self.memory = memory
    

    def response(
        self, 
        model: str, 
        input: str, 
        tools: list | None = None,
        tool_choice: ToolChoice = ToolChoice.NONE,
        instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 65536,
        safety_enabled: bool = True,
        **kwargs
    ) -> tuple[str, str]:
        global_logger.info(f"Processing user input: {input[:50]}...")
        system_message = {"role": "system", "content": instruction if instruction else ""}
        tools = tools if tool_choice != ToolChoice.NONE else None
        # Optional flag to control streaming-style output in adapters
        streaming_output = kwargs.pop("streaming_output", False)
        global_logger.debug(f"streaming_output={streaming_output}")
        
        # Store original input for auditing/memory
        original_input = input
        llm_input = input  # This may be masked version sent to LLM

        # Safety check: optionally block prompt-injection style inputs before calling LLM
        if safety_enabled:
            try:
                is_safe, reason = check_prompt_injection(original_input)
            except Exception as e:
                global_logger.error(f"Error during safety check: {e}")
                is_safe, reason = True, ""

            if not is_safe:
                global_logger.warning(f"Blocked user input due to safety: {reason}")
                # Optionally record the blocked attempt in memory for auditing
                if self.memory is not None:
                    self.memory.add(role="user", content=original_input)
                    self.memory.add(role="assistant", content=f"Yêu cầu bị chặn bởi bộ lọc an toàn: {reason}")
                return "", f"Yêu cầu bị chặn bởi bộ lọc an toàn: {reason}"
            
            # Check for PII in user input
            try:
                detected_pii = check_pii(original_input)
            except Exception as e:
                global_logger.error(f"Error during PII check: {e}")
                detected_pii = {}

        # When safety is enabled, also mask any detected PII before sending to LLM
        if safety_enabled:
            try:
                if detected_pii:
                    masked_input = mask_pii_fn(original_input, detected_pii)
                    llm_input = masked_input
                    global_logger.info(f"[PII MASKED] Input masked before sending to LLM")
            except Exception as e:
                global_logger.error(f"Error during PII masking: {e}")
                llm_input = original_input  # Fallback to original if masking fails

        # Add user message once, before the tool-calling loop
        # Note: Memory stores original input for auditing
        if self.memory is not None:
            self.memory.add(role="user", content=original_input)
        
        while True:
            if self.memory is not None:
                # Sanitize memory messages before sending to the API — only role and content allowed
                raw_messages = self.memory.get_messages()
                sanitized = []
                for m in raw_messages:
                    if isinstance(m, dict):
                        role = m.get("role")
                        content = m.get("content", "")
                        if role == "tool":
                            tool_call_id = m.get("tool_call_id")
                            name = m.get("name")
                            msg = {"role": "tool", "content": content}
                            if tool_call_id is not None:
                                msg["tool_call_id"] = tool_call_id
                            if name is not None:
                                msg["name"] = name
                        else:
                            msg = {"role": role, "content": content}
                    else:
                        msg = {"role": None, "content": str(m)}
                    sanitized.append(msg)
                messages = [system_message] + sanitized
                # Replace the last user message content with masked version for LLM
                if messages and messages[-1].get("role") == "user":
                    messages[-1] = {"role": "user", "content": llm_input}
            else:
                user_message = {"role": "user", "content": llm_input}
                messages = [system_message, user_message]
            response = self.adapter.response(
                model=model, 
                messages=messages, 
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
            last_message = response.choices[0].message
            
            if not last_message.tool_calls:
                global_logger.debug(f"No tool calls, returning assistant response")
                if self.memory is not None:
                    self.memory.add(role="assistant", content=last_message.content)
                # Phần thinking từ reasoning model (DeepSeek-R1, QwQ, o3... trên Groq)
                # Tham chiếu: message.reasoning_content trong response object
                thinking = getattr(last_message, "reasoning_content", None) or ""
                text = last_message.content or ""
                global_logger.debug(f"Response complete – thinking: {len(thinking)} chars, text: {len(text)} chars")
                return thinking, text

            global_logger.debug(f"Tool calls detected: {[tc.function.name for tc in last_message.tool_calls]}")
            if self.memory is not None:
                self.memory.add(role="assistant", content=last_message.content, tool_calls=last_message.tool_calls)

            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                global_logger.debug(f"Executing tool: {tool_name}")
                try:
                    tool_args = json.loads(tool_call.function.arguments) or {}
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
                if self.memory is not None:
                    self.memory.add_tool_message(tool_call, tool_response)