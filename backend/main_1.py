from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from backend.cloud_azure.document_upload import process_document
from backend.cloud_azure.qa_chain import QAChain
from backend.cloud_azure.embeddings import EmbeddingService
from backend.cloud_azure.retrieval import AzureRetriever
from backend.cloud_azure.indexer import AzureSearchIndexer

app = FastAPI()

# Initialize services
embedder = EmbeddingService()
retriever = AzureRetriever()
qa = QAChain()
indexer=AzureSearchIndexer()



@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    pdf_bytes = await file.read()


    doc_name = indexer.sanitize_key(file.filename)

    if indexer.document_exists(doc_name):
        return {
            "status": "exists",
            "document_name": doc_name
        }

    # process only if not exists
    doc_name = process_document(pdf_bytes, doc_name)

    return {
        "status": "processed",
        "document_name": doc_name
    }


class QueryRequest(BaseModel):
    query: str
    document_name: str


@app.post("/ask")
def ask_question(request: QueryRequest):

    query = request.query
    document_name = request.document_name

    # Step 1: Embed query
    query_embedding = embedder.embed_query(query)

    # Step 2: Retrieve relevant chunks
    results = retriever.search(
        query_embedding,
        top_k=3,
        document_name=document_name
    )

    # Step 3: Build context
    context = "\n\n".join([r["content"] for r in results])

    # Step 4: Generate answer
    answer = qa.generate_answer(context, query)

    return {
        "answer": answer,
        "sources": results,
        "context": context
    }