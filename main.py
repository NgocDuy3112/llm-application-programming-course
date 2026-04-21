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

    # Show example
    print("   Example ground truth extraction:")
    for row in ds.select(range(min(3, len(ds)))):
        print(f"     Query: {row['query_vi'][:10]}...")
        print(f"     Ground truth: {row['ground_truth']}\n")

    # --- Build pipeline ---
    print("\n2. Building HuggingFace pipeline...")
    pipe = build_pipeline()
    print(f"   Model: {MODEL_ID}")
    print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}\n")

    # --- Run evaluation ---
    print("3. Running batch evaluation...")
    print(f"   Total samples: {len(ds)}, Batch size: {BATCH_SIZE}\n")

    accuracy_records = []

    # Process batches
    for batch_idx, start in enumerate(range(0, len(ds), BATCH_SIZE), start=1):
        end = min(start + BATCH_SIZE, len(ds))
        batch = ds.select(range(start, end))

        queries = list(batch["query_vi"])
        ground_truths = list(batch["ground_truth"])

        # Generate responses: no-CoT and with-CoT
        print(f"   Batch {batch_idx}: Generating no-CoT responses...")
        no_cot_texts = generate_text_with_prompt(
            pipe, queries, DIRECT_PROMPT, batch_size=BATCH_SIZE
        )

        print(f"   Batch {batch_idx}: Generating CoT responses...")
        cot_texts = generate_text_with_prompt(
            pipe, queries, COT_PROMPT, batch_size=BATCH_SIZE
        )

        # Process results
        correct_no = 0
        correct_cot = 0

        for idx, (q, gt, no_text, cot_text) in enumerate(
            zip(queries, ground_truths, no_cot_texts, cot_texts),
            start=start + 1,
        ):
            ans_no = extract_answer(no_text)
            ans_cot = extract_answer(cot_text)
            match_no = ans_no.strip() == gt.strip()
            match_cot = ans_cot.strip() == gt.strip()

            correct_no += int(match_no)
            correct_cot += int(match_cot)

            print(f"   Sample {idx}")
            print(f"     query_vi: {q}")
            print(f"     non-CoT answer: {ans_no}")
            print(f"     CoT answer: {ans_cot}")

        # Calculate batch accuracy
        batch_total = len(queries)
        acc_no = correct_no / batch_total * 100
        acc_cot = correct_cot / batch_total * 100

        accuracy_records.append({
            "batch_idx": batch_idx,
            "batch_start": start + 1,
            "batch_end": end,
            "model": MODEL_ID,
            "total": batch_total,
            "correct_no_cot": correct_no,
            "correct_cot": correct_cot,
            "accuracy_no_cot": round(acc_no, 4),
            "accuracy_cot": round(acc_cot, 4),
            "accuracy_diff": round(acc_cot - acc_no, 4),
        })

        print(f"   Batch {batch_idx}: No-CoT={acc_no:.1f}% | CoT={acc_cot:.1f}%")

        # Clean up memory
        del no_cot_texts, cot_texts
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # --- Summary ---
    print("\n4. Final Summary")
    total_samples = sum(r["total"] for r in accuracy_records)
    total_correct_no = sum(r["correct_no_cot"] for r in accuracy_records)
    total_correct_cot = sum(r["correct_cot"] for r in accuracy_records)

    overall_acc_no = (total_correct_no / total_samples) * 100 if total_samples > 0 else 0
    overall_acc_cot = (total_correct_cot / total_samples) * 100 if total_samples > 0 else 0

    print(f"   Total samples: {total_samples}")
    print(f"   Accuracy (No CoT): {overall_acc_no:.2f}%")
    print(f"   Accuracy (With CoT): {overall_acc_cot:.2f}%")
    print(f"   Improvement: {overall_acc_cot - overall_acc_no:+.2f}%")
    print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    run()