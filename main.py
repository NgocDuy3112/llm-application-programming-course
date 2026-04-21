import gc
import torch
from transformers import logging as hf_logging

hf_logging.set_verbosity_error()

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

    # --- Run evaluation ---
    print("3. Running batch evaluation...")
    print(f"   Total samples: {len(ds)}, Batch size: {BATCH_SIZE}\n")

    # Process batches
    for batch_idx, start in enumerate(range(0, len(ds), BATCH_SIZE), start=1):
        end = min(start + BATCH_SIZE, len(ds))
        batch = ds.select(range(start, end))

        queries = list(batch["query_vi"])
        ground_truths = list(batch["ground_truth"])

        # Generate responses: no-CoT and with-CoT
        no_cot_texts = generate_text_with_prompt(
            pipe, queries, DIRECT_PROMPT, batch_size=BATCH_SIZE
        )

        cot_texts = generate_text_with_prompt(
            pipe, queries, COT_PROMPT, batch_size=BATCH_SIZE
        )

        for idx, (q, gt, no_text, cot_text) in enumerate(
            zip(queries, ground_truths, no_cot_texts, cot_texts),
            start=start + 1,
        ):
            ans_no = extract_answer(no_text)
            ans_cot = extract_answer(cot_text)

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
    print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    run()