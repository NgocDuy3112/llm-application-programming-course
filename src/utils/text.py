"""Tiện ích phân tích văn bản: trích xuất đáp án từ phản hồi của mô hình."""
import re


def extract_answer(text: str) -> str:
    """Trích xuất con số đáp án từ văn bản phản hồi.

    Ưu tiên mẫu cuối cùng `####{answer}`, sau đó mới dự phòng các dạng số khác.
    """
    # Mẫu: #### {số} ở cuối văn bản (ưu tiên cao nhất)
    m = re.search(r"####\s*([+-]?[\d,]+(?:\.\d+)?)\s*$", text)
    if m:
        return m.group(1).replace(",", "")

    # Mẫu: #### {số} ở bất kỳ vị trí nào trong văn bản
    m = re.search(r"####\s*([+-]?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")

    # Mẫu: "Đáp án là: {số}"
    m = re.search(r"Đáp án là:\s*([+-]?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")

    # Phương án dự phòng: lấy số cuối cùng trong văn bản
    nums = re.findall(r"[+-]?[\d,]+(?:\.\d+)?", text)
    return nums[-1].replace(",", "") if nums else ""
