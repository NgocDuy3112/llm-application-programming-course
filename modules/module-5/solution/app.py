import os
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

    sidebar()
    client = OpenAI(
        api_key=os.getenv("OLLAMA_API_KEY"),
        base_url="https://ollama.com/v1"
    )
    
    # Create service (stateless except for internal config)
    if st.session_state.get("summarization_mode_widget", False):
        chat_service = SummarizationChatService(client=client)
    elif st.session_state.get("sliding_window_mode_widget", False):
        chat_service = SlidingWindowChatService(client=client)
    else:
        chat_service = ChatService(client=client)

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

        try:
            # App owns history: append user message immediately
            user_msg = {"role": "user", "content": user_input}
            st.session_state["chat_history"].append(user_msg)
            redraw_chat_history()
            service_response = chat_service.response(
                model="gpt-oss:20b-cloud",
                instructions=st.session_state.get("custom_instructions", ""),
                input=st.session_state["chat_history"],
                max_output_tokens=st.session_state.get("max_output_tokens", 2048),
                stream=stream_mode,
                temperature=st.session_state.get("temperature", 0.25),
            )
        
            
            # For SummarizationChatService, unpack (new_history, response)
            if isinstance(chat_service, SummarizationChatService):
                new_history, response = service_response
                st.session_state["chat_history"][:] = new_history
            else:
                response = service_response
            
            # Parse response based on stream mode
            if stream_mode:
                stream_slot = st.empty()
                assistant_msg = display_streaming_response(response, stream_slot=stream_slot)
                if assistant_msg:
                    st.session_state["chat_history"].append(assistant_msg)
            else:
                with st.spinner("Đang phản hồi..."):
                    assistant_msg = display_response(response)
                    if assistant_msg:
                        st.session_state["chat_history"].append(assistant_msg)

            redraw_chat_history()

        except Exception as e:
            st.error(f"❌ [ERROR] {str(e)}")
        finally:
            st.session_state["is_generating"] = False



if __name__ == "__main__":
    main()