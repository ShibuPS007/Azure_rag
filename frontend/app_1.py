import streamlit as st
import requests
import os
import uuid

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Azure RAG Chatbot", layout="wide")
st.title("Azure RAG Chatbots")

uploaded_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])

if st.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())

if uploaded_file is not None:
    if (
        "processed_file" not in st.session_state
        or st.session_state["processed_file"] != uploaded_file.name
    ):

        with st.spinner("⚙️ Processing document..."):

            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
            }

            response = requests.post(f"{API_URL}/upload", files=files)

            if response.status_code != 200:
                st.error("Upload failed")
                st.stop()

            data = response.json()
            doc_name = data["document_name"]
            status = data["status"]
        st.session_state.messages = []
        st.session_state["current_doc"] = doc_name
        st.session_state["processed_file"] = uploaded_file.name

        if status == "exists":
            st.info(f"📄 Document already indexed: {doc_name}")
        else:
            st.success(f"✅ Document indexed: {doc_name}")

document_name = st.session_state.get("current_doc")

if not document_name:
    st.warning("Please upload a document first")
    st.stop()

st.info(f"📄 Current document: {document_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask a question about your document...")

if query:

    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Generating answer..."):

        response = requests.post(
            f"{API_URL}/ask",
            json={
                "query": query,
                "document_name": document_name,
                "session_id": st.session_state.session_id
            }
        )

        if response.status_code != 200:
            st.error("Backend error")
            st.stop()

        data = response.json()

        answer = data.get("answer", "")
        results = data.get("sources", [])
        source_type = data.get("source", "unknown")
        score = data.get("score", None)
        decision = data.get("decision", None)

    with st.chat_message("assistant"):
        st.markdown(answer)

        # 🧠 Agent Info (NEW)
        st.caption(f"🧠 Source: {source_type} | Score: {score} | Decision: {decision}")

        # 📄 Sources
        with st.expander("📄 Sources"):
            if results:
                for r in results:
                    st.write(f"Page {r.get('page', '?')} - {r.get('document', '?')}")
            else:
                st.write("No sources available")

    st.session_state.messages.append({"role": "assistant", "content": answer})