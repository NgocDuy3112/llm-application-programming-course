import json
import streamlit as st
from src.core.client import LLMClient
from src.utils.settings import *




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
    with st.sidebar:
        model_provider = st.sidebar.selectbox(
            "Select Provider",
            options=["OpenAI", "Groq", "Gemini", "Ollama", "Huggingface"],
            index=0
        )
        if model_provider in NEED_API_KEY_PROVIDERS:
            api_key = st.sidebar.text_input(
                "API Key",
                value=settings.API_KEY,
                type="password"
            )
        model = st.sidebar.selectbox(
            "Select Model",
            options=MODELS_LIST.get(model_provider, []),
            placeholder="Không có mô hình nào khả dụng",
            index=0
        )
            
        custom_instructions = st.sidebar.text_area(
            "Custom Instructions (optional)",
            value="",
            height=200
        )
        streaming_mode = st.sidebar.checkbox(
            "Enable Streaming Mode",
            value=st.session_state["streaming_mode"],
            key="streaming_mode_widget",
            disabled=st.session_state.get("structured_mode_widget", False)
        )
        structured_output_mode = st.sidebar.checkbox(
            "Enable Structured Output",
            value=False,
            key="structured_mode_widget",
            on_change=lambda: st.session_state.update(streaming_mode=False) if st.session_state["structured_mode_widget"] else None
        )
        output_schema = ""
        if structured_output_mode:
            # Disable streaming mode checkbox
            st.session_state["streaming_mode"] = False
            output_schema_text = st.text_area(
                "Output Schema (JSON format)",
                value='{"field_name": { "type": "str", "default": null, "description": "Description of the field" }}',
                height=300,
            )
            try:
                output_schema = json.loads(output_schema_text)
                st.success("Valid JSON schema")
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
        client = LLMClient(
            model=model, 
            model_provider=model_provider, 
            api_key=api_key, 
        )
    user_input = st.chat_input("Type your message here...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        if structured_output_mode:
            response = client.create_structured_response(
                schema=output_schema,
                input=st.session_state["chat_history"],
                stream=False,
                instructions=custom_instructions
            )
        else:
            response = client.create_response(
                input=st.session_state["chat_history"],
                stream=streaming_mode,
                instructions=custom_instructions
            )
        with st.chat_message("assistant"):
            # if streaming_mode:
            #     full_response = ""
            #     for chunk in response:
            #         delta = chunk.choices[0].delta.get("content", "")
            #         full_response += delta
            #         st.markdown(full_response + "▌")
            #     st.markdown(full_response)
            # else:
                st.markdown(response)



if __name__ == "__main__":
    main()