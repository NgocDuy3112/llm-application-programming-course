## LLM Application Programming Course

Dự án này là một bài thực hành về **Prompt Engineering** với mô hình LLM.

Chương trình chính sẽ:

- đọc dữ liệu từ `data/sample_dataset.xlsx`
- chạy hai chế độ sinh câu trả lời:
  - **non-CoT**
  - **CoT**
- in ra terminal cho từng mẫu:
  - `query_vi`
  - `ground_truth`
  - `non-CoT answer`
  - `CoT answer`

## Yêu cầu

- Python 3.12+
- HuggingFace token để truy cập model `meta-llama/Llama-3.2-1B-Instruct`
- môi trường ảo Python (`.venv`)

## Cài đặt

Từ thư mục gốc của project, tạo môi trường và cài dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cấu hình `.env`

Tạo file `.env` ở thư mục gốc và thêm token:

```env
HF_TOKEN=your_huggingface_token_here
```

Bạn cần chấp nhận điều khoản truy cập model `meta-llama/Llama-3.2-1B-Instruct` trên HuggingFace trước khi chạy.

## Dữ liệu

File đầu vào chính là:

- `data/sample_dataset.xlsx`

File này đã được chuẩn bị sẵn với 2 cột:

- `query_vi`
- `response_vi`

Hiện tại file này chứa **15 câu** và được dùng trực tiếp làm input cho mô hình.

## Chạy chương trình

Chạy từ thư mục gốc:

```bash
python main.py
```

Nếu bạn đang dùng `.venv`, có thể chạy:

```bash
.venv/bin/python main.py
```

## Kết quả

Chương trình sẽ in trực tiếp ra console cho từng câu với các trường:

- `query_vi`
- `ground_truth`
- `non-CoT answer`
- `CoT answer`

## Cấu trúc chính

- `main.py` — chạy pipeline đánh giá
- `src/config.py` — cấu hình model, đường dẫn dữ liệu, thông số sinh text
- `src/data/dataset.py` — đọc dữ liệu từ Excel
- `src/inference/prompts.py` — prompt tiếng Việt cho non-CoT và CoT
- `src/inference/engine.py` — tạo prompt và sinh câu trả lời
- `src/utils/text.py` — trích xuất đáp án từ output

## Ghi chú

- Nếu bạn muốn đổi bộ dữ liệu, chỉ cần thay file `data/sample_dataset.xlsx`.
- Dữ liệu đầu vào phải có ít nhất 2 cột: `query_vi` và `response_vi`.
