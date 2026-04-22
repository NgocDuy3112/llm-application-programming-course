"""Configuration constants and pipeline builder for CoT evaluation."""
import os

import torch
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import pipeline

load_dotenv()


# --- Dataset & Model Configuration ---
DATASET_FILE_PATH = "data/sample_dataset.xlsx"
DATASET_NAME = DATASET_FILE_PATH  # Backward-compatible alias.
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"

# --- Inference Parameters ---
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.1  # Lower for math accuracy


def get_hf_token():
    return os.getenv("HF_TOKEN")


def build_pipeline():
    """Build and return HuggingFace pipeline with proper device and auth."""
    hf_token = get_hf_token()
    if hf_token:
        login(token=hf_token)
    else:
        print("Note: HF_TOKEN not found in environment. Please login manually.")

    device = 0 if torch.cuda.is_available() else -1
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    pipe = pipeline(
        "text-generation",
        model=MODEL_ID,
        device=device,
        dtype=dtype,
    )

    # Llama-style tokenizers often do not define a pad token by default.
    # Batched generation requires one, so reuse EOS and left-pad the inputs.
    if pipe.tokenizer.pad_token_id is None:
        pipe.tokenizer.pad_token = pipe.tokenizer.eos_token
        pipe.tokenizer.pad_token_id = pipe.tokenizer.eos_token_id
    pipe.tokenizer.padding_side = "left"

    return pipe
