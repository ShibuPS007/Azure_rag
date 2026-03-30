from .state import AgentState
from .agent import router_agent, rag_agent, web_agent,evaluator_agent,hybrid_agent
from backend.cloud_azure.document_upload import process_document
from backend.cloud_azure.indexer import AzureSearchIndexer
import os
indexer=AzureSearchIndexer()



def run_test(query,doc_name):
    state = AgentState(
        query=query,
        document_name=doc_name
    )


    print("\n==============================")
    print("🧠 Query:", query)

    # Step 1: Routing
    route = router_agent(state)
    print("🔀 Router:", route)

    state.source = route["source"]

    # Step 2: Execute agent
    if state.source == "rag":
        result = rag_agent(state)
    elif state.source == "web":
        result = web_agent(state)
    elif state.source=="hybrid":
        rag_result=rag_agent(state)

        state.answer=rag_result["answer"]
        result=hybrid_agent(state)
    else:
        result = {"answer": "Invalid source"}
    
    state.answer = result["answer"]

    # Step 3: Output
    print("Answer:", result["answer"])
    print("Source:", result["source"])

    
    eval_result = evaluator_agent(state)
    state.score = eval_result.get("score")
    state.decision = eval_result.get("decision")

    print(f"🧪 Score: {state.score}, Decision: {state.decision}")
     # Step 4: Decision Handling
    if state.decision == "accept":
        final_answer = state.answer

    elif state.decision == "combine":
        print("🔀 Combining RAG + Web...")
        hybrid_result = hybrid_agent(state)
        final_answer = hybrid_result["answer"]

    elif state.decision == "fallback":
        print("🌐 Falling back to Web...")

        web_result = web_agent(state)
        state.answer = web_result["answer"]

        # re-evaluate
        eval_result = evaluator_agent(state)
        final_answer = state.answer

    else:
        final_answer = state.answer

    print("\n✅ FINAL ANSWER:\n", final_answer)

file="backend/ingestion/PS Shibu_Resume.pdf"
with open(file, "rb") as f:
    pdf_bytes = f.read()

doc_name = indexer.sanitize_key(os.path.basename(file))
exists = indexer.document_exists(doc_name)
print("Exists:", exists)
if not exists:
    print("📥 Processing document...")
    process_document(pdf_bytes, doc_name)
else:
    print("✅ Document already indexed")

# 🔹 Run query
run_test("what is this doc and recent updates in devops?", doc_name)