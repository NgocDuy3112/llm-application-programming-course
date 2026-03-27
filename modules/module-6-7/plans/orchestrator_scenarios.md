# DANH SÁCH TÌNH HUỐNG DEMO – LỚP ĐIỀU PHỐI (ORCHESTRATOR)

## 1. Xử lý input & điều hướng hội thoại

### 1.1. Thiếu thông tin → hỏi lại
- Prompt: “Khóa Python giá bao nhiêu?”
- Orchestrator: phát hiện thiếu → hỏi lại
- Insight: LLM không biết khi nào cần hỏi – hệ thống quyết định

### 1.2. Chuẩn hoá input người dùng
- Prompt: “python course price pls??? 😭”
- Orchestrator: clean / chuẩn hoá / translate
- Insight: Input cũng cần xử lý, không chỉ output


## 2. Tích hợp & xử lý dữ liệu

### 2.1. Dữ liệu mâu thuẫn (conflict)
- 2 nguồn giá khác nhau
- Orchestrator: chọn / merge
- Insight: LLM không biết chọn dữ liệu đúng

### 2.2. Multi-source → 1 output
- Lấy từ nhiều file/API khác nhau
- Orchestrator: gom + format
- Insight: Chất lượng output phụ thuộc cách “feed data”


## 3. Điều phối model (linh hoạt hệ thống)

### 3.1. Dynamic routing (chọn model theo task)
- Creative → model A  
- Logic → model B  
- Insight: User không chọn model, hệ thống chọn

### 3.2. Fallback model khi lỗi
- Model A fail → chuyển sang model B
- Insight: Orchestrator đảm bảo hệ thống không “chết”

### 3.3. A/B testing model
- 1 prompt → 2 model
- So sánh output
- Insight: Đánh giá model là trách nhiệm hệ thống


## 4. Kiểm soát & bảo vệ hệ thống

### 4.1. Prompt injection
- Prompt: “Bỏ qua tất cả hướng dẫn…”
- Orchestrator: detect & chặn
- Insight: System prompt không đủ để bảo vệ

### 4.2. Rate limit / chống spam
- Spam nhiều request
- Orchestrator: block / delay
- Insight: Bảo vệ tài nguyên là vai trò của hệ thống

### 4.3. Filter output nguy hiểm
- Prompt độc hại
- Orchestrator: kiểm tra output → chặn
- Insight: Kiểm soát cả sau khi LLM trả lời


## 5. Reliability (độ ổn định hệ thống)

### 5.1. Retry khi lỗi
- Tool/API fail
- Orchestrator: retry / fallback
- Insight: LLM không chịu trách nhiệm reliability

### 5.2. Validate output (JSON)
- Prompt yêu cầu JSON
- Orchestrator: parse → fail → regenerate
- Insight: LLM không đảm bảo đúng format


## 6. Kiểm soát logic nâng cao

### 6.1. Quyết định có dùng tool hay không
- Prompt mơ hồ
- Orchestrator: decide
- Insight: Không phải lúc nào cũng gọi tool

### 6.2. Pipeline nhiều bước
- search → lọc → summarize
- Insight: Orchestrator điều phối toàn bộ pipeline


---

## Gợi ý demo nhanh

Nên chọn 3 tình huống:
1. Thiếu thông tin → hỏi lại  
2. Dynamic routing model  
3. Prompt injection  

---

## Câu chốt

“LLM chỉ là một component  
Thứ quyết định hệ thống thông minh hay không là cách bạn điều phối nó”
