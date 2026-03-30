import streamlit as st
import tempfile

from backend.cloud_azure.embeddings import EmbeddingService
from backend.cloud_azure.retrieval import AzureRetriever
from backend.cloud_azure.qa_chain import QAChain
from backend.cloud_azure.document_upload import process_document



embedder = EmbeddingService()
retriever = AzureRetriever()
qa = QAChain()


st.set_page_config(page_title="Azure RAG Chatbot", layout="wide")
st.title("Azure RAG Chatbot")


uploaded_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])


if uploaded_file is not None:
    if (
        "processed_file" not in st.session_state
        or st.session_state["processed_file"] != uploaded_file.name
    ):

        pdf_bytes = uploaded_file.read()

        with st.spinner("⚙️ Processing document..."):
            doc_name = process_document(pdf_bytes, uploaded_file.name)

        
        st.session_state["current_doc"] = doc_name
        st.session_state["processed_file"] = uploaded_file.name

        st.success(f"✅ Document indexed: {doc_name}")


# to check if doc is uploaded
document_name = st.session_state.get("current_doc")

if not document_name:
    st.warning("Please upload a document first")
    st.stop()

st.info(f"📄 Current document: {document_name}")



# memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# USER INPUT

query = st.chat_input("Ask a question about your document...")

if query:
    
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner(" Thinking..."):
        query_embedding = embedder.embed_query(query)

        
        results = retriever.search(
            query_embedding,
            top_k=3,
            document_name=document_name
        )

       
        context = "\n\n".join([r["content"] for r in results])

       
        answer = qa.generate_answer(context, query)

  
   # RESPONSE
    
    with st.chat_message("assistant"):
        st.markdown(answer)

       
        with st.expander("📄 Sources"):
            for r in results:
                st.write(f"Page {r['page']} - {r['document']}")

        
        with st.expander(" Retrieved Context"):
            st.write(context)

    st.session_state.messages.append({"role": "assistant", "content": answer})