import gc
import torch

from src.config import (
    DATASET_FILE_PATH,
    MODEL_ID,
    BATCH_SIZE,
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
    print("=== Starting Evaluation Pipeline ===\n")

    # --- Load and prepare dataset ---
    print(f"1. Loading dataset from {DATASET_FILE_PATH}...")
    ds = load_dataset_from_excel(DATASET_FILE_PATH)
    print(f"   Dataset loaded with {len(ds)} samples")
    print("   Using the prepared 15-row dataset directly; no further sampling.\n")

    # Add ground truth extracted from response_vi
    ds = add_ground_truth(ds)

    # --- Build pipeline ---
    print("\n2. Building HuggingFace pipeline...")
    pipe = build_pipeline()
    print(f"   Model: {MODEL_ID}")
    print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}\n")

    # --- Run evaluation (single batch) ---
    print("3. Running evaluation on all samples in a single batch...")
    print(f"   Total samples: {len(ds)}\n")

    # Counters for overall accuracy
    total_evaluated = 0
    total_correct_no = 0
    total_correct_cot = 0

    if len(ds) == 0:
        print("   No samples to evaluate.")
    else:
        # Prepare all queries at once
        queries = list(ds["query_vi"])
        ground_truths = list(ds["ground_truth"])

        # Generate responses for all queries in one call each
        print("   Generating no-CoT responses for all samples...")
        no_cot_texts = generate_text_with_prompt(
            pipe, queries, DIRECT_PROMPT, batch_size=len(queries)
        )

        print("   Generating CoT responses for all samples...")
        cot_texts = generate_text_with_prompt(
            pipe, queries, COT_PROMPT, batch_size=len(queries)
        )

        for idx, (q, gt, no_text, cot_text) in enumerate(
            zip(queries, ground_truths, no_cot_texts, cot_texts), start=1
        ):
            # Trích xuất đáp án số từ output (chỉ chấp nhận marker ####)
            ans_no = extract_answer(no_text)
            ans_cot = extract_answer(cot_text)

            gt_str = (gt or "").strip()
            ans_no_str = (ans_no or "").strip()
            ans_cot_str = (ans_cot or "").strip()

            match_no = ans_no_str == gt_str
            match_cot = ans_cot_str == gt_str

            total_correct_no += int(match_no)
            total_correct_cot += int(match_cot)
            total_evaluated += 1

            print(f"   Sample {idx}")
            print(f"     query_vi: {q}")
            print(f"     ground_truth: {gt}")
            print(f"     non-CoT answer: {ans_no}")
            print(f"     CoT answer: {ans_cot}")

        # Clean up memory
        del no_cot_texts, cot_texts
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # --- Summary ---
    print("\n4. Final Summary")
    print(f"   Total samples processed: {len(ds)}")
    if total_evaluated > 0:
        acc_no = total_correct_no / total_evaluated * 100
        acc_cot = total_correct_cot / total_evaluated * 100
    else:
        acc_no = acc_cot = 0.0

    print(f"   Accuracy (No CoT): {acc_no:.2f}% ({total_correct_no}/{total_evaluated})")
    print(f"   Accuracy (With CoT): {acc_cot:.2f}% ({total_correct_cot}/{total_evaluated})")
    print(f"   Improvement: {acc_cot - acc_no:+.2f}%")

    print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    run()