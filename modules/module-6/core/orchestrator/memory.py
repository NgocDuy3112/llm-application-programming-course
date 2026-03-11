class WindowMemory:
    def __init__(self, k=5):
        self.k = k
        self.buffer = []

    def add(self, role, content=None, tool_calls=None):
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.buffer.append(msg)
    
    def add_tool_message(self, tool_call, content):
        self.buffer.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": str(content)
        })

    def get_messages(self):
        num_messages = 2 * self.k
        recent_messages = self.buffer[-num_messages:]
        return recent_messages