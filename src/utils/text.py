import re


def extract_answer(text: str) -> str:
    """Extract the answer number from the response text.

    Prefer the final `####{answer}` pattern, then fallback to other numeric forms.
    """
    # Pattern: ####{number} at end of text (highest priority)
    m = re.search(r"####\s*([+-]?[\d,]+(?:\.\d+)?)\s*$", text)
    if m:
        return m.group(1).replace(",", "")

    # Pattern: ####{number} anywhere in text
    m = re.search(r"####\s*([+-]?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")

    # Pattern: "Đáp án là: {number}"
    m = re.search(r"Đáp án là:\s*([+-]?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")

    # Fallback: extract last number in text
    nums = re.findall(r"[+-]?[\d,]+(?:\.\d+)?", text)
    return nums[-1].replace(",", "") if nums else ""
