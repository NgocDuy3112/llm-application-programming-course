import json
from openai import OpenAI



class ChatService:
    def __init__(self, client: OpenAI, history: list | None = None):
        """
        Khởi tạo cơ bản cho ChatService.
        Gợi ý: Lưu trữ client OpenAI và conversation_history (mặc định là list rỗng nếu chưa có).
        """
        # TODO: Cấu hình conversation_history từ list được truyền vào (nếu có)
        self.client = client
        self.conversation_history = history if history is not None else []

    def _convert_response_to_dict(self, response):
        """
        Trích xuất nội dung từ OpenAI Response Object sang dictionary chuẩn hỗ trợ 'reasoning_content' và 'content'.
        Gợi ý: Lặp qua response.output, kiểm tra block.type ('reasoning' hoặc 'message') để lấy block.content[0].text.
        """
        # TODO 2.3: Trích xuất 'reasoning' (lưu vào message_dict["reasoning_content"])
        # TODO 2.4: Trích xuất 'message' (lưu vào message_dict["content"])
        message_dict = {"role": "assistant"}
        return message_dict

    def response(self, model: str, instructions: str, input: str | dict, **kwargs):
        """
        Xử lý tin nhắn của user và gọi OpenAI Responses API (Preview).
        Gợi ý: 
        1. Parse input thành format message dictionary {"role": "user", "content": ...}.
        2. Append user message vào self.conversation_history.
        3. Gọi self.client.responses.create với model, instructions và input là conversation_history.
        4. Nếu stream=False (mặc định), parse response sang dict và append vào history trước khi trả về.
        """
        # TODO 2.1: Chuẩn bị tin nhắn User {"role": "user", "content": ...} và append vào lịch sử
        # TODO 2.2: Gọi API client.responses.create (Lưu ý: tham số 'input' nhận vào list messages)
        # TODO 2.5: Nếu không stream, parse kết quả và cập nhật lịch sử. Trả về message_dict.
        pass


class SlidingWindowChatService(ChatService):
    def __init__(self, client: OpenAI, window_size: int = 10, history: list | None = None):
        """
        Cửa sổ trượt: Chỉ gửi một số lượng tin nhắn gần nhất làm ngữ cảnh.
        """
        # TODO 4.2: Gọi super().__init__ và lưu window_size
        super().__init__(client, history)
        self.window_size = window_size

    def response(self, model: str, instructions: str, input: str | dict, **kwargs):
        """
        Gợi ý: Cắt lịch sử hội thoại (self.conversation_history[-window_size:]) trước khi gửi cho Responses API.
        """
        # TODO 4.3: Thêm user message vào history gốc (giống ChatService.response)
        # TODO 4.4: Lấy window_size tin nhắn cuối cùng để làm ngữ cảnh gửi API qua tham số 'input'
        # TODO 4.5: Lưu kết quả phản hồi của Assistant vào history gốc (full list)
        pass


class SummarizationChatService(ChatService):
    def __init__(self, client: OpenAI, summary_turn_threshold: int = 10, keep_last: int = 1, history: list | None = None):
        """
        Nén ngữ cảnh: Tóm tắt các tin nhắn cũ khi đạt ngưỡng số lượt chat.
        """
        # TODO 5.2: Khởi tạo các tham số ngưỡng (threshold) và số tin nhắn giữ lại (keep_last)
        # TODO 5.3: Khởi tạo biến lưu trữ bản tóm tắt tích lũy (history_summary)
        super().__init__(client, history)
        self.history_summary = ""

    def _compress_history(self, model, messages_to_summarize):
        """
        Gợi ý: Tạo một prompt yêu cầu AI tóm tắt 'messages_to_summarize' dựa trên 'self.history_summary' cũ.
        Cập nhật kết quả vào self.history_summary.
        """
        # TODO 5.4: Format transcript từ danh sách tin nhắn (vd: 'User: hello, Assistant: hi')
        # TODO 5.5: Gọi API tạo tóm tắt mới (khuyên dùng OpenAI completion thông thường)
        pass

    def response(self, model: str, instructions: str, input: str | dict, **kwargs):
        """
        Gợi ý: 
        1. Kiểm tra số lượt chat (ví dụ đếm số tin nhắn 'user').
        2. Nếu vượt threshold, tách phần cũ mang đi nén và chỉ giữ lại 'keep_last' tin nhắn thực tế.
        3. Chèn 'self.history_summary' vào cuối chuỗi instructions gửi lên API.
        """
        # TODO 5.6: Kiểm tra ngưỡng và thực hiện nén nếu đạt (Gọi self._compress_history)
        # TODO 5.7: Bổ sung bối cảnh tóm tắt (self.history_summary) vào 'instructions'
        # TODO 5.8: Gọi Responses API và cập nhật lịch sử thực tế
        pass
