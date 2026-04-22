SOLUTION_START = "####"
SOLUTION_END = ""
REASONING_START = "<thought>"
REASONING_END = "</thought>"


# TODO[BT1a]: Viết system prompt cho chế độ trả lời TRỰC TIẾP (không có Chain-of-Thought).
#
#   Yêu cầu:
#     1. Giao vai trò rõ ràng cho model (agent description).
#     2. Mô tả đầu vào – bài toán bằng tiếng Việt.
#     3. Chỉ định định dạng đầu ra – chỉ xuất đáp án số, đặt sau SOLUTION_START.
#     4. Cấm model giải thích hay trình bày bước làm.
#
#   Lưu ý: dùng f-string để nhúng SOLUTION_START / SOLUTION_END vào prompt.
DIRECT_PROMPT = f"""
"""

# TODO[BT1b]: Viết system prompt cho chế độ Chain-of-Thought (CoT).
#
#   Yêu cầu:
#     1. Giao vai trò như TODO (1).
#     2. Yêu cầu model suy luận từng bước bằng tiếng Việt TRƯỚC khi đưa ra đáp án.
#     3. Phần suy luận phải được bọc giữa REASONING_START và REASONING_END.
#     4. Đáp án số cuối cùng đặt sau SOLUTION_START (và trước SOLUTION_END nếu có).
#
#   Gợi ý cấu trúc:
#     [Vai trò]
#     [Mô tả đầu vào]
#     Bước 1 – Suy luận: đặt trong {REASONING_START} ... {REASONING_END}
#     Bước 2 – Đáp án:   đặt sau {SOLUTION_START}
COT_PROMPT = f"""
"""