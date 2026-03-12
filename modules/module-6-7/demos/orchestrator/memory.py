from logger import global_logger


class WindowMemory:
    def __init__(self, k=5):
        global_logger.debug(f"Initializing WindowMemory with k={k}")
        self.k = k
        self.buffer = []

    def add(self, role, content=None, tool_calls=None):
        global_logger.debug(f"Adding message: role={role}, content_length={len(content) if content else 0}")
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
            global_logger.debug(f"Message includes {len(tool_calls)} tool calls")
        self.buffer.append(msg)
    
    def add_tool_message(self, tool_call, content):
        global_logger.debug(f"Adding tool message for {tool_call.function.name}")
        self.buffer.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": str(content)
        })

    def get_messages(self):
        num_messages = 2 * self.k
        recent_messages = self.buffer[-num_messages:]
        global_logger.debug(f"Retrieving {len(recent_messages)} recent messages from buffer (total: {len(self.buffer)})")
        return recent_messages