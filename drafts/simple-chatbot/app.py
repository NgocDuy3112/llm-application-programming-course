import json
import streamlit as st
from src.core.client import OpenAIStandardClient
from src.utils.settings import *


THINKING_PROCESS_DISPLAY_STRING = "🧠 Quá trình suy luận"


def _chain_first(first_item, iterator):
    yield first_item
    yield from iterator


def sidebar():
    with st.sidebar:
        model_provider = st.sidebar.selectbox(
            "Chọn nhà cung cấp mô hình",
            options=["Groq", "Gemini", "Ollama", "Huggingface"],
            index=0,
        )

        api_key = None
        if model_provider in NEED_API_KEY_PROVIDERS:
            api_key = st.sidebar.text_input(
                "Nhập API Key",
                value=settings.API_KEY,
                type="password",
            )

        model = st.sidebar.selectbox(
            "Chọn mô hình",
            options=MODELS_LIST.get(model_provider, []),
            placeholder="Không có mô hình nào khả dụng",
            index=0,
        )

        temperature = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
        )

        max_output_tokens = st.sidebar.slider(
            "Số tokens tối đa",
            min_value=1,
            max_value=2048,
            value=512,
            step=1,
        )

        custom_instructions = st.sidebar.text_area(
            "Chỉ dẫn tùy chỉnh (tùy chọn)",
            value="",
            height=200,
        )

        streaming_mode = st.sidebar.checkbox(
            "Bật chế độ Streaming",
            value=st.session_state["streaming_mode"],
            key="streaming_mode_widget",
            disabled=st.session_state.get("structured_mode_widget", False),
        )

        structured_output_mode = st.sidebar.checkbox(
            "Bật chế độ Đầu ra Cấu trúc",
            value=st.session_state.get("structured_mode_widget", False),
            key="structured_mode_widget",
            on_change=(
                lambda: st.session_state.update(streaming_mode=False)
                if st.session_state["structured_mode_widget"]
                else None
            ),
        )

        output_schema = ""
        if structured_output_mode:
            # Disable streaming mode checkbox
            st.session_state["streaming_mode"] = False
            streaming_mode = False
            output_schema_text = st.text_area(
                "Lược đồ Đầu ra (định dạng JSON)",
                value='{"field_name": { "type": "str", "default": null, "description": "Description of the field" }}',
                height=300,
            )
            try:
                output_schema = json.loads(output_schema_text)
                st.success("Lược đồ hợp lệ!")
            except json.JSONDecodeError:
                st.error("Định dạng JSON không hợp lệ. Vui lòng kiểm tra lại.")

        client = OpenAIStandardClient(
            model=model,
            model_provider=model_provider,
            api_key=api_key,
        )

    state = {
        "streaming_mode": streaming_mode,
        "structured_output_mode": structured_output_mode,
        "output_schema": output_schema,
        "custom_instructions": custom_instructions,
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
    }
    return client, state


def stream(response, spinner_text: str) -> str:
    response_iter = iter(response)
    with st.spinner(spinner_text):
        try:
            first_chunk = next(response_iter)
        except StopIteration:
            first_chunk = None

    if first_chunk is None:
        st.markdown("")
        return ""

    thinking_expander = st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False)
    thinking_ph = thinking_expander.empty()
    message_ph = st.empty()
    full_text = ""
    full_reasoning = ""

    for chunk in _chain_first(first_chunk, response_iter):
        ctype = chunk.get("type") if isinstance(chunk, dict) else "text"
        content = chunk.get("content") if isinstance(chunk, dict) else str(chunk)
        if ctype == "reasoning":
            full_reasoning += content
            thinking_ph.markdown(full_reasoning)
        else:
            full_text += content
            message_ph.markdown(full_text + "▌")

    if full_reasoning:
        thinking_ph.markdown(full_reasoning)
    message_ph.markdown(full_text)
    return full_text



def main():
    st.title("Simple Chatbot Application")
    # widen the sidebar via injected CSS
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { width: 420px; min-width: 420px; }
        .css-1d391kg { width: 420px; }
        /* shift main content to avoid overlap */
        main { margin-left: 440px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Get session state history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "streaming_mode" not in st.session_state:
        st.session_state["streaming_mode"] = True
    client, sidebar_state = sidebar()
    # Render existing chat history in main area
    for msg in st.session_state.get("chat_history", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # show a thinking expander above each assistant message (collapsed)
        
        with st.chat_message(role):
            if role == "assistant":
                with st.expander(THINKING_PROCESS_DISPLAY_STRING, expanded=False):
                    st.write("")
            st.markdown(content)

    user_input = st.chat_input("Type your message here...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        streaming_mode = sidebar_state["streaming_mode"]
        structured_output_mode = sidebar_state["structured_output_mode"]
        output_schema = sidebar_state["output_schema"]
        custom_instructions = sidebar_state["custom_instructions"]
        max_output_tokens = sidebar_state["max_output_tokens"]
        temperature = sidebar_state["temperature"]

        spinner_text = "Vui lòng chờ trong giây lát..."

        # Non-streaming: show spinner while waiting for the full response.
        if not streaming_mode:
            with st.spinner(spinner_text):
                if structured_output_mode:
                    response = client.create_structured_response(
                        schema=output_schema,
                        input=st.session_state["chat_history"],
                        stream=streaming_mode,
                        instructions=custom_instructions,
                        max_output_tokens=max_output_tokens,
                        temperature=temperature,
                    )
                else:
                    response = client.create_response(
                        input=st.session_state["chat_history"],
                        stream=streaming_mode,
                        instructions=custom_instructions,
                        max_output_tokens=max_output_tokens,
                        temperature=temperature,
                    )

            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state["chat_history"].append({"role": "assistant", "content": response})
            return

        # Streaming: show spinner until the first chunk arrives.
        if structured_output_mode:
            response = client.create_structured_response(
                schema=output_schema,
                input=st.session_state["chat_history"],
                stream=streaming_mode,
                instructions=custom_instructions,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
            )
        else:
            response = client.create_response(
                input=st.session_state["chat_history"],
                stream=streaming_mode,
                instructions=custom_instructions,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
            )

        with st.chat_message("assistant"):
            full_text = stream(response, spinner_text)
            if full_text == "":
                st.session_state["chat_history"].append({"role": "assistant", "content": ""})
                return

        # store only assistant message in history (do not store reasoning)
        st.session_state["chat_history"].append({"role": "assistant", "content": full_text})



if __name__ == "__main__":
    main()