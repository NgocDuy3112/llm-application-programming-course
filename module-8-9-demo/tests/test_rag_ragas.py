"""
Đánh giá hệ thống RAG bằng RAGAS (Retrieval Augmented Generation Assessment).

4 Metrics chính:
  1. Faithfulness     — Câu trả lời có trung thực với context không? (không bịa)
  2. Answer Relevancy — Câu trả lời có liên quan đến câu hỏi không?
  3. Context Precision — Trong các context retrieved, bao nhiêu thực sự hữu ích?
  4. Context Recall    — Context retrieved có chứa đủ thông tin so với ground_truth?

Yêu cầu:
  - File eval_dataset.json đã được sinh bởi generate_eval_data.py
  - GROQ_API_KEY trong .env
  - Cài đặt: pip install ragas datasets langchain-openai langchain-huggingface

Chạy: cd sample-chatbot && python tests/test_rag_ragas.py
"""

import os
import sys
import json
import time
from datetime import datetime

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True)

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    LLMContextPrecisionWithoutReference,
    LLMContextRecall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings


# ================================================================
# CẤU HÌNH
# ================================================================

EVAL_DATASET_FILE = os.path.join(
    os.path.dirname(__file__), "data_samples", "eval_dataset.json"
)

RESULTS_FILE = os.path.join(
    os.path.dirname(__file__), "data_samples", "eval_results.json"
)

# Model dùng cho RAGAS judge
GROQ_MODEL = "llama-3.1-8b-instant"

# Embedding model (giống RAG pipeline)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "AITeamVN/Vietnamese_Embedding_v2")


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def load_eval_dataset(filepath: str) -> list[dict]:
    """Đọc eval_dataset.json."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def create_ragas_llm():
    """
    Tạo LLM wrapper cho RAGAS sử dụng Groq API.
    Cấu hình timeout dài hơn và max_tokens lớn hơn để tránh lỗi.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY không tìm thấy trong .env")

    llm = ChatOpenAI(
        model=GROQ_MODEL,
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0.2,
        max_tokens=4096,
        timeout=180,           # Tăng timeout lên 180s
        max_retries=3,         # Tự retry khi timeout
        model_kwargs={"n": 1}, # Groq chỉ hỗ trợ n=1
    )
    return LangchainLLMWrapper(llm)


def create_ragas_embeddings():
    """Tạo Embedding wrapper cho RAGAS dùng cùng model với RAG pipeline."""
    hf_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return LangchainEmbeddingsWrapper(hf_embeddings)


def convert_to_ragas_format(eval_data: list[dict]) -> Dataset:
    """
    Chuyển đổi eval_dataset.json sang format RAGAS 0.2.x.

    RAGAS cần 4 cột:
      - user_input:          câu hỏi (str)
      - response:            câu trả lời của hệ thống (str)
      - retrieved_contexts:  danh sách context retrieved (list[str])
      - reference:           ground truth / đáp án chuẩn (str)
    """
    ragas_data = {
        "user_input": [],
        "response": [],
        "retrieved_contexts": [],
        "reference": [],
    }

    for item in eval_data:
        if not item.get("answer", "").strip():
            print(f"  ⚠️  Bỏ qua (answer rỗng): {item['question'][:60]}...")
            continue

        ragas_data["user_input"].append(item["question"])
        ragas_data["response"].append(item["answer"])
        ragas_data["retrieved_contexts"].append(item["contexts"])
        ragas_data["reference"].append(item["ground_truth"])

    return Dataset.from_dict(ragas_data)


# ================================================================
# MAIN
# ================================================================

def run_evaluation():
    """Pipeline đánh giá RAG bằng RAGAS."""

    print("=" * 60)
    print("🧪 RAGAS EVALUATION - Đánh giá hệ thống RAG")
    print("=" * 60)

    # ---- 1. Đọc eval dataset ----
    print(f"\n📂 Đọc eval dataset: {EVAL_DATASET_FILE}")
    if not os.path.exists(EVAL_DATASET_FILE):
        print(f"❌ Không tìm thấy file: {EVAL_DATASET_FILE}")
        print("   Chạy generate_eval_data.py trước!")
        return

    eval_data = load_eval_dataset(EVAL_DATASET_FILE)
    print(f"   ✅ {len(eval_data)} mẫu\n")

    # ---- 2. Chuyển đổi sang format RAGAS ----
    print("🔄 Chuyển đổi sang format RAGAS...")
    dataset = convert_to_ragas_format(eval_data)
    print(f"   ✅ {len(dataset)} mẫu hợp lệ\n")

    if len(dataset) == 0:
        print("❌ Không có mẫu nào hợp lệ để đánh giá!")
        return

    # ---- 3. Cấu hình LLM + Embeddings cho RAGAS ----
    print("🤖 Cấu hình RAGAS judge...")
    ragas_llm = create_ragas_llm()
    ragas_embeddings = create_ragas_embeddings()
    print(f"   ✅ LLM: {GROQ_MODEL}")
    print(f"   ✅ Embeddings: {EMBEDDING_MODEL}\n")

    # ---- 4. Định nghĩa metrics ----
    # Bỏ AnswerRelevancy vì Groq không hỗ trợ n>1 (RAGAS cần n=3 cho metric này)
    metrics = [
        Faithfulness(llm=ragas_llm),
        LLMContextPrecisionWithoutReference(llm=ragas_llm),
        LLMContextRecall(llm=ragas_llm),
    ]

    print("📏 Metrics:")
    print("   1. Faithfulness")
    print("   2. Context Precision")
    print("   3. Context Recall")
    print("   ⚠️  AnswerRelevancy bị bỏ qua (Groq không hỗ trợ n>1)\n")

    # ---- 5. Chạy đánh giá ----
    print("-" * 60)
    print("🚀 Bắt đầu đánh giá (có thể mất vài phút)...\n")

    start_time = time.time()

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        raise_exceptions=False,  # Không crash khi 1 sample lỗi
    )

    elapsed = time.time() - start_time

    # ---- 6. In kết quả tổng hợp ----
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ ĐÁNH GIÁ RAGAS")
    print(f"   ⏱️  Thời gian: {elapsed:.1f}s")
    print("=" * 60)

    # RAGAS 0.2.x: dùng .to_pandas() để lấy kết quả
    df = result.to_pandas()

    # Lấy các cột metric (loại bỏ cột data)
    data_cols = {"user_input", "response", "retrieved_contexts", "reference"}
    metric_cols = [col for col in df.columns if col not in data_cols]

    # Điểm trung bình
    print(f"\n{'Metric':<35} {'Avg Score':>10}")
    print("-" * 47)

    avg_scores = {}
    for col in metric_cols:
        scores = df[col].dropna()
        if len(scores) > 0:
            avg = scores.mean()
            avg_scores[col] = round(float(avg), 4)
            emoji = "✅" if avg >= 0.7 else "⚠️" if avg >= 0.5 else "❌"
            print(f"  {emoji} {col:<32} {avg:>8.4f}")

    # ---- 7. Chi tiết từng câu hỏi ----
    print(f"\n{'─' * 60}")
    print("📋 CHI TIẾT TỪNG CÂU HỎI:")
    print(f"{'─' * 60}\n")

    for i, row in df.iterrows():
        question = row.get("user_input", "N/A")
        print(f"[{i+1}] ❓ {question[:80]}")
        for col in metric_cols:
            val = row[col]
            if val is not None and str(val) != "nan":
                val = float(val)
                emoji = "✅" if val >= 0.7 else "⚠️" if val >= 0.5 else "❌"
                print(f"    {emoji} {col}: {val:.4f}")
            else:
                print(f"    ⚠️  {col}: N/A (lỗi khi đánh giá)")
        print()

    # ---- 8. Lưu kết quả ----
    # Convert DataFrame để serialize JSON
    per_sample = []
    for _, row in df.iterrows():
        sample = {}
        for col in df.columns:
            val = row[col]
            if col in data_cols:
                sample[col] = str(val)[:200]  # Truncate data columns
            else:
                sample[col] = round(float(val), 4) if val is not None and str(val) != "nan" else None
        per_sample.append(sample)

    results_output = {
        "timestamp": datetime.now().isoformat(),
        "model": GROQ_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "num_samples": len(dataset),
        "elapsed_seconds": round(elapsed, 1),
        "aggregate_scores": avg_scores,
        "per_sample": per_sample,
    }

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results_output, f, ensure_ascii=False, indent=2, default=str)

    print(f"💾 Kết quả đã lưu vào: {RESULTS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()
