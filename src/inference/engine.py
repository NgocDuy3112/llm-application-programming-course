"""Text generation engine: pipeline inference and output decoding."""
from src.config import (
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P,
    REPETITION_PENALTY,
    PIPE_BATCH_SIZE,
)


def decode_pipe_output(outputs):
    """Decode outputs from HuggingFace pipeline to list of text strings."""
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


def generate_text_with_prompt(pipe, prompts, system_prompt: str, batch_size: int = PIPE_BATCH_SIZE):
    """Generate text using chat template with system prompt.

    Args:
        pipe: HuggingFace pipeline
        prompts: List of user prompts
        system_prompt: System message for the model
        batch_size: Batch size for pipeline

    Returns:
        List of generated text strings
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
        top_p=TOP_P,
        repetition_penalty=REPETITION_PENALTY,
        return_full_text=False,
        batch_size=batch_size,
    )

    return decode_pipe_output(outputs)
