import re
import streamlit as st

from orchestrator.tools import DEFAULT_TOOLS
from logger import global_logger
from custom_types import ToolChoice



def render_chat_interface(engine: object):
    global_logger.debug("Rendering chat interface")
    st.title("Xây dựng chatbot cơ bản")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.container():
        for entry in st.session_state.chat_history:
            with st.chat_message(entry["role"]):
                # Show reasoning/"suy luận" above the assistant message when available
                if entry.get("thinking") and entry.get("role") == "assistant":
                    with st.expander("💭 SUY LUẬN", expanded=False):
                        st.markdown(entry["thinking"])
                st.markdown(entry["content"])
        global_logger.debug(f"Displayed {len(st.session_state.chat_history)} messages from chat history")

    user_input = st.chat_input("Nhập tin nhắn của bạn ở đây...", key="chat_input")
    if user_input:
        # Extract any <think>...</think> blocks from the user's input and treat them as manual reasoning
        think_matches = re.findall(r"<think>(.*?)</think>", user_input, flags=re.DOTALL | re.IGNORECASE)
        user_thinking = "\n\n".join(m.strip() for m in think_matches).strip() if think_matches else ""
        # Remove the <think> blocks from the visible message sent to the model/UI
        cleaned_input = re.sub(r"<think>.*?</think>", "", user_input, flags=re.DOTALL | re.IGNORECASE).strip()
        visible_user_msg = cleaned_input if cleaned_input else "[Phần suy nghĩ nội bộ đã được tách ra]"

        global_logger.debug(f"Processing user input: {visible_user_msg[:50]}...")
        with st.chat_message("user"):
            st.markdown(visible_user_msg)

        # Only append to UI chat_history, engine.memory handles its own buffer
        st.session_state.chat_history.append({"role": "user", "content": visible_user_msg})

        # Send cleaned input (without <think> blocks) to the model
        thinking_from_model, assistant_reply = engine.response(
            model=st.session_state.selected_model,
            input=cleaned_input,
            temperature=st.session_state.temperature,
            tools=DEFAULT_TOOLS if st.session_state.enable_tools else None,
            tool_choice=ToolChoice.AUTO if st.session_state.enable_tools else ToolChoice.NONE,
            max_tokens=st.session_state.max_tokens,
            instruction=st.session_state.instruction,
            safety_enabled=st.session_state.get("enable_safety_filter", True),
            streaming_output=st.session_state.get("streaming_output", False),
        )

        # If the assistant reply itself contains <think> tags, extract them and remove from visible text
        reply_think_matches = re.findall(r"<think>(.*?)</think>", assistant_reply, flags=re.DOTALL | re.IGNORECASE)
        reply_thinking = "\n\n".join(m.strip() for m in reply_think_matches).strip() if reply_think_matches else ""
        assistant_reply_clean = re.sub(r"<think>.*?</think>", "", assistant_reply, flags=re.DOTALL | re.IGNORECASE).strip()

        # Combine user-provided thinking, model reasoning (from response()), and any reply <think> into a single reasoning block
        reasoning_parts: list[str] = []
        if user_thinking:
            reasoning_parts.append(user_thinking)
        if thinking_from_model:
            reasoning_parts.append(thinking_from_model)
        if reply_thinking:
            reasoning_parts.append(reply_thinking)
        combined_thinking = "\n\n".join(reasoning_parts).strip()

        global_logger.debug(f"Assistant reply generated, length: {len(assistant_reply_clean)}")
        with st.chat_message("assistant"):
            # Show reasoning (suy luận) above the visible assistant reply
            if combined_thinking:
                with st.expander("💭 SUY LUẬN", expanded=False):
                    st.markdown(combined_thinking)
            st.markdown(assistant_reply_clean)

        # Only append to UI chat_history, engine.memory handles its own buffer
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply_clean, "thinking": combined_thinking})
        global_logger.debug(f"Updated chat history, total messages: {len(st.session_state.chat_history)}")