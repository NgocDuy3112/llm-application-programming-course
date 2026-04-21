"""Main orchestration script for CoT evaluation.

Loads dataset, evaluates model with and without CoT, saves results to Excel and CSV.
"""
import datetime
import gc

import openpyxl
import torch

from src.config import (
    DATASET_NAME,
    MODEL_ID,
    BATCH_SIZE,
    OUTPUT_FILE_TEMPLATE,
    DATASET_EXCEL_TEMPLATE,
    ACCURACY_CSV_TEMPLATE,
    build_pipeline,
)
from src.inference.prompts import (
    SYSTEM_PROMPT_DIRECT_VI,
    SYSTEM_PROMPT_COT_VI,
)
from src.utils.file_io import save_dataset_to_excel, save_accuracy_to_csv
from src.utils.text import extract_answer
from src.data.dataset import load_dataset_from_hf, sample_dataset, add_ground_truth
from src.inference.engine import generate_text_with_prompt


def run():
    """Main evaluation pipeline."""
    print("=== Starting Colab Evaluation Pipeline ===\n")

    # Generate timestamp for outputs
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_excel_path = DATASET_EXCEL_TEMPLATE.format(timestamp=timestamp)
    output_file = OUTPUT_FILE_TEMPLATE.format(timestamp=timestamp)
    accuracy_csv_path = ACCURACY_CSV_TEMPLATE.format(timestamp=timestamp)

    # --- Load and prepare dataset ---
    print("1. Loading dataset...")
    ds_full = load_dataset_from_hf(DATASET_NAME)
    print(f"   Dataset loaded with {len(ds_full)} samples")

    # Sample random subset for evaluation
    num_samples = min(500, len(ds_full))
    ds = sample_dataset(ds_full, num_samples)
    print(f"   Selected {num_samples} random samples for evaluation\n")

    # Add ground truth extracted from response_vi
    ds = add_ground_truth(ds)

    # Show example
    print("   Example ground truth extraction:")
    for row in ds.select(range(min(3, len(ds)))):
        print(f"     Query: {row['query_vi'][:50]}...")
        print(f"     Ground truth: {row['ground_truth']}\n")

    # Save full dataset to Excel
    print(f"2. Saving dataset to {dataset_excel_path}...")
    save_dataset_to_excel(ds, dataset_excel_path)

    # --- Build pipeline ---
    print("\n3. Building HuggingFace pipeline...")
    pipe = build_pipeline()
    print(f"   Model: {MODEL_ID}")
    print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}\n")

    # --- Run evaluation ---
    print("4. Running batch evaluation...")
    print(f"   Total samples: {len(ds)}, Batch size: {BATCH_SIZE}\n")

    accuracy_records = []
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet(title=MODEL_ID.replace("/", "_"))

    # Write headers
    headers = [
        "Sample #",
        "query_vi",
        "response_vi (ground truth)",
        "response_no_cot",
        "answer_no_cot",
        "ground_truth_answer",
        "match_no_cot",
        "response_with_cot",
        "answer_with_cot",
        "match_with_cot",
    ]
    ws.append(headers)

    # Process batches
    for batch_idx, start in enumerate(range(0, len(ds), BATCH_SIZE), start=1):
        end = min(start + BATCH_SIZE, len(ds))
        batch = ds.select(range(start, end))

        queries = list(batch["query_vi"])
        ground_truths = list(batch["ground_truth"])
        original_responses = list(batch["response_vi"])

        # Generate responses: no-CoT and with-CoT
        print(f"   Batch {batch_idx}: Generating no-CoT responses...")
        no_cot_texts = generate_text_with_prompt(
            pipe, queries, SYSTEM_PROMPT_DIRECT_VI, batch_size=BATCH_SIZE
        )

        print(f"   Batch {batch_idx}: Generating CoT responses...")
        cot_texts = generate_text_with_prompt(
            pipe, queries, SYSTEM_PROMPT_COT_VI, batch_size=BATCH_SIZE
        )

        # Process results
        correct_no = 0
        correct_cot = 0

        for idx, (q, orig_resp, gt, no_text, cot_text) in enumerate(
            zip(queries, original_responses, ground_truths, no_cot_texts, cot_texts),
            start=start + 1,
        ):
            ans_no = extract_answer(no_text)
            ans_cot = extract_answer(cot_text)
            match_no = ans_no.strip() == gt.strip()
            match_cot = ans_cot.strip() == gt.strip()

            correct_no += int(match_no)
            correct_cot += int(match_cot)

            # Write row to Excel
            ws.append([
                idx,
                q,
                orig_resp,
                no_text,
                ans_no,
                gt,
                "Đúng" if match_no else "Sai",
                cot_text,
                ans_cot,
                "Đúng" if match_cot else "Sai",
            ])

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

    # --- Save results ---
    print(f"\n5. Saving results...")
    wb.save(output_file)
    print(f"   Results saved to {output_file}")

    save_accuracy_to_csv(accuracy_records, accuracy_csv_path)
    print(f"   Accuracy stats saved to {accuracy_csv_path}")

    # --- Summary ---
    print("\n6. Final Summary")
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
