import streamlit as st

st.set_page_config(page_title="AI Email Assistant", layout="wide")

st.title("🤖 AI Email Assistant Dashboard")

st.subheader("System Status")
st.success("AI System Running")


# 🔹 Display logs
st.subheader("System Logs")

try:
    with open("logs.txt", "r", encoding="utf-8") as f:
        logs = f.read()

    st.text_area("Logs", logs, height=400)

except:
    st.warning("No logs available yet")


# 🔹 About section
st.subheader("Project Overview")

st.write("""
This AI Email Assistant uses:
- Ollama
- TinyLlama
- Retrieval-Augmented Generation (RAG)
- Prompt Injection Protection
- Logging and Monitoring

The system classifies emails into:
- NORMAL
- SPAM
- TRASH

It can automatically generate professional replies.
""")