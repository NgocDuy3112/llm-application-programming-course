import gc
import torch

from src.config import (
    DATASET_FILE_PATH,
    MODEL_ID,
    build_pipeline,
)
from src.inference.prompts import (
    DIRECT_PROMPT,
    COT_PROMPT,
)
from src.utils.text import extract_answer
from src.data.dataset import load_dataset_from_excel, add_ground_truth
from src.inference.engine import generate_text_with_prompt


def run():
    print("=== Bắt đầu quy trình đánh giá ===\n")

    # --- Tải và chuẩn bị bộ dữ liệu ---
    print(f"1. Tải bộ dữ liệu từ {DATASET_FILE_PATH}...")
    ds = load_dataset_from_excel(DATASET_FILE_PATH)
    print(f"   Số mẫu trong bộ dữ liệu: {len(ds)}")
    print("   Đang tải dữ liệu...\n")

    # Thêm nhãn đúng trích xuất từ response_vi
    ds = add_ground_truth(ds)

    # --- Tạo pipeline ---
    print("\n2. Gọi pipeline mô hình...")
    pipe = build_pipeline()
    print(f"   Mô hình: {MODEL_ID}")
    print(f"   Thiết bị: {'GPU' if torch.cuda.is_available() else 'CPU'}\n")

    # --- Chạy đánh giá ---
    print("3. Chạy đánh giá trên toàn bộ mẫu trong một batch...")
    print(f"   Tổng số mẫu: {len(ds)}\n")

    # Bộ đếm độ chính xác tổng thể
    total_evaluated = 0
    total_correct_no = 0
    total_correct_cot = 0

    if len(ds) == 0:
        print("   Không có mẫu nào để đánh giá.")
    else:
        # Chuẩn bị toàn bộ câu hỏi cùng lúc
        queries = list(ds["query_vi"])
        ground_truths = list(ds["ground_truth"])

        # Sinh câu trả lời cho toàn bộ câu hỏi trong một lần gọi mỗi chế độ
        print("   Đang tạo câu trả lời không CoT cho tất cả mẫu...")
        no_cot_texts = generate_text_with_prompt(
            pipe, queries, DIRECT_PROMPT, batch_size=len(queries)
        )

        print("   Đang tạo câu trả lời CoT cho tất cả mẫu...")
        cot_texts = generate_text_with_prompt(
            pipe, queries, COT_PROMPT, batch_size=len(queries)
        )

        for idx, (q, gt, no_text, cot_text) in enumerate(
            zip(queries, ground_truths, no_cot_texts, cot_texts), start=1
        ):
            # TODO[BT2]: Gọi hàm extract_answer để trích xuất đáp án số từ no_text và cot_text.
            ans_no = ...
            ans_cot = ...
            
            # Chuẩn hóa chuỗi để so sánh (loại bỏ khoảng trắng thừa)
            gt_str = (gt or "").strip()
            ans_no_str = (ans_no or "").strip()
            ans_cot_str = (ans_cot or "").strip()

            # TODO[BT2]: Cập nhật bộ đếm độ chính xác tổng thể dựa trên kết quả so sánh vào hai biến total_correct_no và total_correct_cot.
            # Gợi ý: so sánh gt_str với ans_no_str và ans_cot_str, nếu trùng khớp thì tăng bộ đếm tương ứng lên 1.

            total_evaluated += 1

            print(f"   Mẫu {idx}")
            print(f"     câu hỏi_vi: {q}")
            print(f"     đáp án chuẩn: {gt_str}")
            print(f"     đáp án không CoT: {ans_no_str}")
            print(f"     đáp án CoT: {ans_cot_str}")

        # Dọn dẹp bộ nhớ
        del no_cot_texts, cot_texts
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # --- Tóm tắt ---
    print("\n4. Tóm tắt cuối cùng")
    print(f"   Tổng số mẫu đã xử lý: {len(ds)}")
    # TODO[BT2]: Tính toán độ chính xác cho cả hai chế độ và in ra kết quả cuối cùng.
    

    print("\n=== Hoàn tất đánh giá ===")


if __name__ == "__main__":
    run()