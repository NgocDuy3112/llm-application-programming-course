"""
Script sinh bộ eval dataset cho đánh giá RAG bằng RAGAS.

Workflow:
  1. Đọc file Excel chứa question + ground_truth (do bạn soạn)
  2. Với mỗi câu hỏi → gọi RAG retrieve → lấy contexts
  3. Gọi LLM (Groq) với contexts → sinh answer
  4. Lưu tất cả vào eval_dataset.json

Yêu cầu:
  - Đã upload tài liệu vào Knowledge Base qua Streamlit UI
  - File Excel có 2 cột: question, ground_truth
  - Có GROQ_API_KEY trong .env

Chạy: cd sample-chatbot && python tests/generate_eval_data.py
"""

import os
import sys
import json
import time

# Thêm thư mục gốc vào path để import các module của project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True)

import pandas as pd
from openai import OpenAI

from orchestrator.rag import SimpleRAG


# ================================================================
# CẤU HÌNH — Sửa tại đây nếu cần
# ================================================================

# File input: Excel chứa question + ground_truth
QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "data_samples", "questions.xlsx")

# File output: JSON chứa question + ground_truth + answer + contexts
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "data_samples", "eval_dataset.json")

# Model dùng để sinh answer
GROQ_MODEL = "openai/gpt-oss-20b"

# RAG config (lấy từ .env, giống app.py)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "AITeamVN/Vietnamese_Embedding_v2")
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# RAG retrieve params
# SEARCH_TOP_K = 10
# RERANK_TOP_K = 4


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def create_llm_client() -> OpenAI:
    """Tạo OpenAI client trỏ đến Groq API."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY không tìm thấy trong .env")
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )


def call_llm(client: OpenAI, question: str, context: str) -> str:
    """
    Gọi LLM với context để sinh câu trả lời.
    Prompt yêu cầu LLM chỉ trả lời dựa trên context (không bịa).
    """
    prompt = f"""Chủ thể: Bạn là Trợ lý Ảo chuyên gia về Nhân sự và Pháp chế của Công ty Cổ phần Cấp nước Trung An.
    Nhiệm vụ: Trả lời các thắc mắc của người lao động dựa TRÊN DUY NHẤT tài liệu "Nội quy lao động" được cung cấp trong ngữ cảnh (context).

    Khai thác dữ liệu:
    1. LUÔN LUÔN trích dẫn chính xác số Điều, Khoản và Mục khi đưa ra thông tin (Ví dụ: "Theo Điều 4, Khoản 3.1...").
    2. Nếu câu hỏi không có trong tài liệu, hãy trả lời lịch sự: "Rất tiếc, nội dung này không được quy định trong Nội quy lao động hiện tại. Vui lòng liên hệ phòng TCHC để được giải đáp chi tiết."
    3. Tuyệt đối KHÔNG tự ý suy diễn hoặc dùng kiến thức bên ngoài về Luật Lao động chung nếu tài liệu nội bộ có quy định riêng biệt (Ví dụ: Số ngày nghỉ kết hôn trong nội quy là 04 ngày, khác với quy định tối thiểu 03 ngày của luật chung).

    Ngôn ngữ và Phong cách:
    - Ngôn ngữ: Tiếng Việt, chuyên nghiệp, rõ ràng, dễ hiểu nhưng vẫn giữ tính pháp lý.
    - Cấu trúc: Sử dụng bullet points để liệt kê các điều kiện hoặc hình thức kỷ luật.
    - Định dạng: Bôi đậm các con số quan trọng (ngày nghỉ, mức tiền, thời hạn).

    Cảnh báo bảo mật: Không tiết lộ các thông tin nằm trong danh mục bảo mật tuyệt đối trừ khi người truy vấn có thẩm quyền.

Context:
{context}

Câu hỏi: {question}

Trả lời:"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=4096,
    )
    return response.choices[0].message.content


def parse_contexts(raw_context: str) -> list[str]:
    """
    Tách context string (từ rag.retrieve()) thành list các đoạn riêng lẻ.
    
    Input:  "[Tài liệu 1]\n..." + "---" + "[Tài liệu 2]\n..." 
    Output: ["[Tài liệu 1]\n...", "[Tài liệu 2]\n..."]
    """
    parts = raw_context.split("\n\n---\n\n")
    return [part.strip() for part in parts if part.strip()]


# ================================================================
# MAIN
# ================================================================

def generate_dataset():
    """Pipeline chính: đọc câu hỏi → retrieve → generate answer → lưu file."""

    print("=" * 60)
    print("📊 GENERATE EVAL DATASET")
    print("=" * 60)

    # ---- 1. Đọc câu hỏi từ Excel ----
    print(f"\n📂 Đọc câu hỏi từ: {QUESTIONS_FILE}")
    if not os.path.exists(QUESTIONS_FILE):
        print(f"❌ Không tìm thấy file: {QUESTIONS_FILE}")
        print("   Hãy đặt file Excel vào thư mục tests/data_samples/")
        return

    df = pd.read_excel(QUESTIONS_FILE)

    # Kiểm tra cột bắt buộc
    required_cols = {"question", "ground_truth"}
    if not required_cols.issubset(df.columns):
        print(f"❌ File Excel cần có 2 cột: question, ground_truth")
        print(f"   Các cột hiện có: {list(df.columns)}")
        return

    # Bỏ dòng trống
    df = df.dropna(subset=["question", "ground_truth"])
    questions_data = df.to_dict(orient="records")
    print(f"   ✅ {len(questions_data)} câu hỏi\n")

    # ---- 2. Khởi tạo RAG ----
    print("🔧 Khởi tạo RAG pipeline...")
    rag = SimpleRAG(
        collection_name="knowledge_base",
        embedding_model_name=EMBEDDING_MODEL,
        cross_encoder_model_name=CROSS_ENCODER_MODEL,
        chroma_path=CHROMA_PATH,
    )
    print(f"   ✅ Knowledge base: {rag.doc_count()} chunks\n")

    if rag.doc_count() == 0:
        print("❌ Knowledge base trống!")
        print("   Hãy upload tài liệu qua Streamlit UI trước (streamlit run app.py)")
        return

    # ---- 3. Khởi tạo LLM client ----
    print("🤖 Khởi tạo LLM client (Groq)...")
    client = create_llm_client()
    print(f"   ✅ Model: {GROQ_MODEL}\n")

    # ---- 4. Sinh answer + contexts cho từng câu hỏi ----
    print("-" * 60)
    eval_dataset = []

    for i, qa in enumerate(questions_data, 1):
        question = str(qa["question"]).strip()
        ground_truth = str(qa["ground_truth"]).strip()

        print(f"[{i}/{len(questions_data)}] ❓ {question}")

        # Retrieve contexts từ RAG
        raw_context = rag.retrieve(question)
        contexts = parse_contexts(raw_context)
        print(f"   📚 Retrieved {len(contexts)} contexts")

        # Sinh answer từ LLM
        try:
            answer = call_llm(client, question, raw_context)
            print(f"   💬 Answer: {answer[:100]}...")
        except Exception as e:
            print(f"   ❌ LLM error: {e}")
            answer = f"Error: {e}"

        eval_dataset.append({
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "contexts": contexts,
        })

        # Tránh rate limit Groq
        time.sleep(1)
        print()

    # ---- 5. Lưu dataset ----
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(eval_dataset, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"✅ Đã lưu {len(eval_dataset)} mẫu vào: {OUTPUT_FILE}")
    print("=" * 60)

    # ---- 6. Preview ----
    print("\n📋 Preview 2 mẫu đầu tiên:\n")
    for sample in eval_dataset[:2]:
        print(f"  Q: {sample['question']}")
        print(f"  A: {sample['answer'][:150]}...")
        print(f"  GT: {sample['ground_truth'][:150]}...")
        print(f"  Contexts: {len(sample['contexts'])} đoạn")
        print()



if __name__ == "__main__":
    generate_dataset()