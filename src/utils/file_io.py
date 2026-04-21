"""File I/O utilities: save results to Excel and CSV."""
import csv

import openpyxl


def save_dataset_to_excel(ds, path: str):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet(title="dataset")
    headers = list(ds.column_names)
    ws.append(headers)
    for row in ds:
        ws.append([row.get(col, "") for col in headers])
    wb.save(path)
    print(f"Saved dataset to {path}")


def save_accuracy_to_csv(records, path: str):
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "batch_idx",
                "batch_start",
                "batch_end",
                "model",
                "total",
                "correct_no_cot",
                "correct_cot",
                "accuracy_no_cot",
                "accuracy_cot",
                "accuracy_diff",
            ],
        )
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved accuracy CSV to {path}")
