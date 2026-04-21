"""Dataset loading, sampling, and preprocessing utilities."""
import random

from datasets import load_dataset

from src.utils.text import extract_answer


def load_dataset_from_hf(dataset_name: str):
    return load_dataset(dataset_name, split="train")


def sample_dataset(ds, num_samples: int):
    num_samples = min(num_samples, len(ds))
    indices = random.sample(range(len(ds)), num_samples)
    return ds.select(indices)


def add_ground_truth(ds):
    return ds.map(
        lambda example: {"ground_truth": extract_answer(example["response_vi"])},
        remove_columns=[],
    )
