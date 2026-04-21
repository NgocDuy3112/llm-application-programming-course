"""Configuration constants and pipeline builder for CoT evaluation."""
import torch
from huggingface_hub import login
from transformers import pipeline

try:
    from google.colab import userdata
    IS_COLAB = True
except ImportError:
    IS_COLAB = False

# --- Dataset & Model Configuration ---
DATASET_NAME = "5CD-AI/Vietnamese-meta-math-MetaMathQA-40K-gg-translated"
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
BATCH_SIZE = 5
PIPE_BATCH_SIZE = 5

# --- File Output Templates ---
OUTPUT_FILE_TEMPLATE = "cot_results_{timestamp}.xlsx"
DATASET_EXCEL_TEMPLATE = "dataset_{timestamp}.xlsx"
ACCURACY_CSV_TEMPLATE = "cot_accuracy_{timestamp}.csv"

# --- Inference Parameters ---
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.1  # Lower for math accuracy
TOP_P = 0.95
REPETITION_PENALTY = 1.1


def get_hf_token():
    """Get HuggingFace token from Colab Secrets or user input."""
    if IS_COLAB:
        try:
            return userdata.get("HF_TOKEN")
        except Exception:
            return None
    return None


def build_pipeline():
    """Build and return HuggingFace pipeline with proper device and auth."""
    hf_token = get_hf_token()
    if hf_token:
        login(token=hf_token)
    else:
        print("Note: HF_TOKEN not found in Colab Secrets. Please login manually.")
        if IS_COLAB:
            login()

    device = 0 if torch.cuda.is_available() else -1
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    pipe = pipeline(
        "text-generation",
        model=MODEL_ID,
        device=device,
        torch_dtype=dtype,
    )
    return pipe
