from src.config import (
    MAX_NEW_TOKENS,
    TEMPERATURE,
)


def decode_pipe_output(outputs):
    """Giải mã đầu ra từ pipeline HuggingFace thành danh sách chuỗi văn bản."""
    texts = []
    for out in outputs:
        if isinstance(out, dict) and "generated_text" in out:
            texts.append(out["generated_text"])
        elif isinstance(out, list) and len(out) > 0 and "generated_text" in out[0]:
            texts.append(out[0]["generated_text"])
        elif isinstance(out, str):
            texts.append(out)
        else:
            texts.append(str(out))
    return texts


def generate_text_with_prompt(pipe, prompts, system_prompt: str, batch_size: int = 10):
    """Sinh văn bản bằng chat template với system prompt.

    Args:
        pipe: Pipeline HuggingFace
        prompts: Danh sách prompt của người dùng
        system_prompt: Thông điệp hệ thống cho mô hình
        batch_size: Kích thước batch cho pipeline

    Returns:
        Danh sách chuỗi văn bản được sinh ra
    """
    formatted_prompts = []
    for user_prompt in prompts:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        prompt_str = pipe.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        formatted_prompts.append(prompt_str)

    outputs = pipe(
        formatted_prompts,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        return_full_text=False,
        batch_size=batch_size,
    )

    return decode_pipe_output(outputs)
