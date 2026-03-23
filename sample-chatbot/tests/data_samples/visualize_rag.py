import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(page_title="RAG Evaluation Visualizer", layout="wide")

st.title("🔍 RAG Pipeline Evaluation Dashboard")

# Load data
@st.cache_data
def load_data():
    # Lấy đường dẫn thư mục chứa file này
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'eval_dataset.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    data = load_data()
    
    # Sidebar for selection
    st.sidebar.header("Navigation")
    question_idx = st.sidebar.selectbox(
        "Select a Question to Review",
        range(len(data)),
        format_func=lambda i: f"Q{i+1}: {data[i]['question'][:50]}..."
    )

    # Main content area
    col1, col2 = st.columns([1, 1])

    current_item = data[question_idx]

    with col1:
        st.subheader("❓ Question")
        st.info(current_item['question'])
        
        st.subheader("✅ Ground Truth (Expected)")
        st.success(current_item['ground_truth'])

    with col2:
        st.subheader("🤖 AI Answer")
        if current_item['answer']:
            st.warning(current_item['answer'])
        else:
            st.error("⚠️ EMPTY ANSWER")

    st.divider()

    st.subheader("📄 Retrieved Contexts")
    for idx, ctx in enumerate(current_item['contexts']):
        with st.expander(f"Context {idx + 1}"):
            st.text(ctx)

    # Summary table
    st.divider()
    st.subheader("📊 Overview Table")
    df = pd.DataFrame(data)
    st.dataframe(df[['question', 'answer']], use_container_width=True)

except FileNotFoundError:
    st.error("Could not find 'eval_dataset.json'. Please make sure the file is in the same directory.")
