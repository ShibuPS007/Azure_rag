from .graph import build_graph
from .state import AgentState
from backend.cloud_azure.document_upload import process_document
from backend.cloud_azure.indexer import AzureSearchIndexer
import os

# Initialize graph
graph = build_graph()

# Load document
file = "backend/ingestion/PS Shibu_Resume.pdf"

with open(file, "rb") as f:
    pdf_bytes = f.read()

indexer = AzureSearchIndexer()
doc_name = indexer.sanitize_key(os.path.basename(file))

# Check indexing
exists = indexer.document_exists(doc_name)
print("Exists:", exists)

if not exists:
    print("📥 Processing document...")
    process_document(pdf_bytes, doc_name)
else:
    print("✅ Document already indexed")


# 🔥 TEST QUERY
state = AgentState(
    query="what is this doc and any recent new technology updates in devops?",
    document_name=doc_name
)

print("\n==============================")
print("🧠 Query:", state.query)

# 🚀 RUN GRAPH
result = graph.invoke(state)

print("\n==============================")
print("✅ FINAL RESULT:\n")

print("Answer:", result["answer"])
print("Source:", result.get("source"))
print("Score:", result.get("score"))
print("Decision:", result.get("decision"))