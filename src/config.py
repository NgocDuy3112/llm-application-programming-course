"""Các hằng cấu hình và bộ tạo pipeline cho phần đánh giá CoT."""
import os

import torch
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import pipeline

load_dotenv()


# --- Cấu hình bộ dữ liệu và mô hình ---
DATASET_FILE_PATH = "data/sample_dataset.xlsx"
DATASET_NAME = DATASET_FILE_PATH  # Bí danh để tương thích ngược.
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
BATCH_SIZE = 5
PIPE_BATCH_SIZE = 5

# --- Tham số suy luận ---
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.1  # Giảm xuống để tăng độ chính xác khi làm toán.
TOP_P = 0.95


def get_hf_token():
    return os.getenv("HF_TOKEN")


def build_pipeline():
    """Tạo và trả về pipeline HuggingFace với thiết bị và xác thực phù hợp."""
    hf_token = get_hf_token()
    if hf_token:
        login(token=hf_token)
    else:
        print("Lưu ý: Không tìm thấy HF_TOKEN trong môi trường. Vui lòng đăng nhập thủ công.")

    device = 0 if torch.cuda.is_available() else -1
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    pipe = pipeline(
        "text-generation",
        model=MODEL_ID,
        device=device,
        dtype=dtype,
    )

    # Bộ tách token kiểu Llama thường không định nghĩa pad token mặc định.
    # Sinh theo batch cần token này, nên dùng lại EOS và đệm trái cho đầu vào.
    if pipe.tokenizer.pad_token_id is None:
        pipe.tokenizer.pad_token = pipe.tokenizer.eos_token
        pipe.tokenizer.pad_token_id = pipe.tokenizer.eos_token_id
    pipe.tokenizer.padding_side = "left"

    return pipe
