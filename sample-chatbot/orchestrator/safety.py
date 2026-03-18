# core/orchestrator/safety.py

import re
from logger import global_logger

# Các pattern injection phổ biến — đủ để demo, không cần exhaustive
INJECTION_PATTERNS = [
    r"bỏ qua.*(hướng dẫn|lệnh|instruction)",
    r"ignore.*(previous|all|prior).*(instruction|prompt|rule)",
    r"pretend.*(you are|you're|to be)",
    r"đóng vai.*(không có hạn chế|không bị giới hạn|AI tự do)",
    r"reveal.*(system prompt|your prompt|your instruction)",
    r"tiết lộ.*(system prompt|hướng dẫn)",
    r"override.*(system|prompt|instruction)",
    r"forget.*(everything|all|your)",
    # Security-related / long-running software patterns
    r"bypass.*(auth|authentication|login|captcha|rate.?limit|security)",
    r"(hack|hacking|how to hack|bẻ khóa|hack vào|tấn công).+",
    r"(steal|đánh cắp|lấy cắp|exfiltrat|exfil).+\s(password|credentials|api|api.?key|token|secret|mật khẩu|khóa|thông tin)",
    r"(exfiltrate|exfil|exfiltrat).+(data|file|information|dữ liệu)",
    r"(persist|persistence|duy trì|lưu.*vĩnh viễn|giữ.*lại).*",
    r"(run.*(background|daemon|forever|continuously)|chạy.*(ngầm|liên tục|mãi|vĩnh viễn))",
    r"(disable|vô hiệu hóa|tắt).*(update|patch|cập nhật|bản vá|security)",
    r"(privileg|escalat|chiếm.*quyền|tăng.*quyền|nâng.*quyền)",
    r"(remote code execution|rce|command injection|command.*injection|thực thi.*từ.*xa)",
    r"(sql injection|xss|cross[- ]site|chèn.*sql|chèn.*mã)",
    r"(bypass.*firewall|vượt.*tường.*lửa|vượt.*bảo mật)",
    r"(install|cài).*(backdoor|malware|mã độc)",
    r"(brute[- ]?force|credential stuffing|đoán.*mật khẩu|đánh.*bằng.*mật khẩu)",
    r"(keylogger|rootkit|trojan|virus|worm|mã độc|malware)",
]

# PII (Personally Identifiable Information) detection patterns
PII_PATTERNS = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,19}\b",  # 13-19 digit card numbers
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",  # US Social Security Number
    "IP_ADDRESS": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "PASSPORT": r"\b[A-Z]{1,2}\d{6,9}\b",  # Passport number format
    "BANK_ACCOUNT": r"\b\d{8,17}\b",  # Bank account (8-17 digits)
}


def check_prompt_injection(user_input: str) -> tuple[bool, str]:
    """
    Returns: (is_safe, reason)
    - is_safe=True  → cho qua Orchestrator → LLM
    - is_safe=False → chặn tại Orchestrator, không gọi LLM
    """
    text = user_input.lower().strip()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            global_logger.warning(f"Phát hiện nội dung không hợp lệ (pattern: `{pattern}`)")
            return False, f"Phát hiện nội dung không hợp lệ (pattern: `{pattern}`)"

    return True, ""


def check_pii(user_input: str) -> dict[str, list[str]]:
    """
    Detect Personally Identifiable Information (PII) in user input.
    
    Returns: Dictionary with PII types as keys and matched values as list
    Examples:
        {"EMAIL": ["user@example.com"], "PHONE": ["123-456-7890"]}
        {} if no PII detected
    """
    detected_pii = {}
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, user_input)
        if matches:
            detected_pii[pii_type] = matches
            # Log each detected PII type
            for match in matches:
                global_logger.warning(
                    f"[PII DETECTED] Type: {pii_type} | Pattern: {match}"
                )
    
    return detected_pii


def mask_pii(user_input: str, detected_pii: dict[str, list[str]] | None = None) -> str:
    """
    Mask Personally Identifiable Information in user input and return masked string.
    
    Args:
        user_input: The user input to mask
        detected_pii: Pre-detected PII dict (optional). If None, will detect first.
    
    Returns:
        masked_input (str): the input with any detected PII replaced by placeholders
    
    Examples:
        "Email: user@example.com, Phone: 123-456-7890"
        → "Email: [EMAIL], Phone: [PHONE]"
    """
    if detected_pii is None:
        detected_pii = check_pii(user_input)
    
    masked_input = user_input
    mask_summary = {}
    
    # Process each PII type with counter
    for pii_type, pattern in PII_PATTERNS.items():
        if pii_type not in detected_pii or not detected_pii[pii_type]:
            continue
        
        # Replace each match with masked version
        masked_input = re.sub(
            pattern,
            f"[{pii_type}]",
            masked_input,
            flags=re.IGNORECASE
        )
        count = len(detected_pii[pii_type])
        mask_summary[pii_type] = count
        
        global_logger.info(f"[PII MASKED] Masked {count} {pii_type}(s)")
    
    return masked_input



