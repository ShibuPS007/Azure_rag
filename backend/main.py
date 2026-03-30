from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from backend.cloud_azure.document_upload import process_document
# from backend.cloud_azure.qa_chain import QAChain
# from backend.cloud_azure.embeddings import EmbeddingService
# from backend.cloud_azure.retrieval import AzureRetriever
from backend.cloud_azure.indexer import AzureSearchIndexer
from backend.agents.graph import build_graph
from backend.agents.state import AgentState

app = FastAPI()

# Initialize services
graph = build_graph()

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
    history: list = []


@app.post("/ask")
def ask_question(request: QueryRequest):

    state = AgentState(
        query=request.query,
        document_name=request.document_name
    )

    # Run full agent system
    result = graph.invoke(state)

    return {
        "answer": result.get("answer"),
        "source": result.get("source"),
        "score": result.get("score"),
        "decision": result.get("decision"),
        "sources": result.get("sources")
    }