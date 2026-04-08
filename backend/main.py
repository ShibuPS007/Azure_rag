from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os
import time
from backend.cloud_azure.document_upload import process_document
# from backend.cloud_azure.qa_chain import QAChain
# from backend.cloud_azure.embeddings import EmbeddingService
# from backend.cloud_azure.retrieval import AzureRetriever
from backend.cloud_azure.indexer import AzureSearchIndexer
from backend.agents.graph import build_graph
from backend.agents.state import AgentState
from backend.logging_guard.logger import log_event,generate_ids
from backend.logging_guard.prompt_injection import detect_prompt_injection
from azure.monitor.opentelemetry import configure_azure_monitor
from backend.logging_guard.hallucination import detect_hallucination
import logging
logging.getLogger("azure").setLevel(logging.WARNING)

configure_azure_monitor(
    connection_string="InstrumentationKey=934893d6-eef8-4844-aa21-d8b474d1cc56;IngestionEndpoint=https://centralindia-0.in.applicationinsights.azure.com/;LiveEndpoint=https://centralindia.livediagnostics.monitor.azure.com/;ApplicationId=73e408e6-f577-40e1-8796-c94d032196c3"
)

app = FastAPI()

# Initialize services
graph = build_graph()

indexer=AzureSearchIndexer()


@app.get("/")
def home():
    return {"message": "RAG API running"}

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
    session_id: str


@app.post("/ask")
def ask_question(request: QueryRequest):

    session_id = request.session_id
    _,question_id = generate_ids()
    is_injection = detect_prompt_injection(request.query)

    if is_injection:
        log_event({
            "session_id": session_id,
            "question_id": question_id,
            "query": request.query,
            "answer": answer,
            "source": result.get("source"),
            "score": result.get("score"),
            "decision": result.get("decision"),
            "prompt_injection": False
        })

        return {
            "answer": "⚠️ Unsafe query detected",
            "source": "blocked"
        }

    state = AgentState(
        query=request.query,
        document_name=request.document_name
    )

    # Run full agent system
    start_time = time.time()

    result = graph.invoke(state)

    latency = time.time() - start_time
    answer = result.get("answer", "")
    context = result.get("context", "")

    hallucination_flag = False

    if context:
        hallucination_flag = detect_hallucination(
            request.query,
            context,
            answer
        )

    log_event({
        "session_id": session_id,
        "question_id": question_id,
        "query": request.query,
        "answer": answer,
        "source": result.get("source"),
        "score": result.get("score"),
        "decision": result.get("decision"),
        "latency": latency,
        "prompt_injection": False,
        "hallucination": hallucination_flag
    })

    return {
        "answer": result.get("answer"),
        "source": result.get("source"),
        "score": result.get("score"),
        "decision": result.get("decision"),
        "sources": result.get("sources")
    }