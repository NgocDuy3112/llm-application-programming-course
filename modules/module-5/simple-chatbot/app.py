import os
from rich import print
from dotenv import load_dotenv

from ui.sidebar import *
from service.chat import *


load_dotenv(dotenv_path="../.env", override=True)



def main():
    st.title("Xây dựng chatbot đơn giản")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False

    # Clean up accidental duplicates while preserving list reference.
    history = st.session_state["chat_history"]
    if history:
        def _msg_key(message: dict) -> tuple:
            return (
                message.get("role"),
                message.get("content"),
                message.get("reasoning_content", ""),
            )

        # Pass 1: remove exact consecutive duplicate messages.
        deduped_history = []
        previous_key = None
        for msg in history:
            key = _msg_key(msg)
            if key != previous_key:
                deduped_history.append(msg)
            previous_key = key

        # Pass 2: remove duplicated adjacent 2-message turns:
        # [user, assistant, user, assistant] where pair 1 == pair 2.
        cleaned_history = []
        i = 0
        while i < len(deduped_history):
            if i + 3 < len(deduped_history):
                a1, a2, b1, b2 = (
                    deduped_history[i],
                    deduped_history[i + 1],
                    deduped_history[i + 2],
                    deduped_history[i + 3],
                )
                if _msg_key(a1) == _msg_key(b1) and _msg_key(a2) == _msg_key(b2):
                    cleaned_history.extend([a1, a2])
                    i += 4
                    continue

            cleaned_history.append(deduped_history[i])
            i += 1

        history[:] = cleaned_history

    sidebar()
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    if st.session_state.get("summarization_mode_widget", False):
        chat_service = SummarizationChatService(client=client, history=st.session_state["chat_history"])
    elif st.session_state.get("sliding_window_mode_widget", False):
        chat_service = SlidingWindowChatService(client=client, history=st.session_state["chat_history"])
    else:
        chat_service = ChatService(client=client, history=st.session_state["chat_history"])

    chat_slot = st.empty()

    def redraw_chat_history():
        chat_slot.empty()
        with chat_slot.container():
            render_chat_history(st.session_state["chat_history"])

    redraw_chat_history()

    user_input = st.chat_input(
        placeholder="Nhập tin nhắn của bạn...",
        key="user_input",
        disabled=st.session_state.get("is_generating", False)
    )

    if user_input:
        st.session_state["is_generating"] = True
        stream_mode = st.session_state.get("streaming_mode_widget", False)
        history_before = len(st.session_state["chat_history"])

        try:
            if stream_mode:
                response = chat_service.response(
                    input=user_input,
                    model="openai/gpt-oss-20b",
                    instructions=st.session_state.get("custom_instructions", ""),
                    max_output_tokens=st.session_state.get("max_output_tokens", 2048),
                    stream=True,
                    temperature=st.session_state.get("temperature", 0.25)
                )

                # Show user message first (appended by service) before assistant stream.
                redraw_chat_history()

                stream_slot = st.empty()
                assistant_msg = display_streaming_response(response, stream_slot=stream_slot)
                if assistant_msg:
                    st.session_state["chat_history"].append(assistant_msg)

            else:
                with st.spinner("Đang phản hồi..."):
                    response = chat_service.response(
                        input=user_input,
                        model="openai/gpt-oss-20b",
                        instructions=st.session_state.get("custom_instructions", ""),
                        max_output_tokens=st.session_state.get("max_output_tokens", 2048),
                        stream=False,
                        temperature=st.session_state.get("temperature", 0.25)
                    )

                # Fallback: if service didn't append assistant in some edge cases,
                # parse response and append manually.
                expected_len = history_before + 2
                if len(st.session_state["chat_history"]) < expected_len:
                    assistant_msg = display_response(response)
                    if assistant_msg:
                        st.session_state["chat_history"].append(assistant_msg)

            # Final render for both modes (replace temp streaming bubble if any).
            redraw_chat_history()

        except Exception as e:
            st.error(f"❌ [ERROR] {str(e)}")
        finally:
            st.session_state["is_generating"] = False



if __name__ == "__main__":
    main()