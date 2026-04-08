from .embeddings import EmbeddingService
from .retrieval import AzureRetriever
from .qa_chain import QAChain

embedder = EmbeddingService()
retriever = AzureRetriever()
qa = QAChain()

query = "What are my technical skills?"

query_embedding = embedder.embed_query(query)

results = retriever.search(
    query_embedding,
    top_k=3,
    document_name="PS_Shibu_Resume_pdf"
)


context = "\n\n".join([r["content"] for r in results])

print("\n----CONTEXT-----\n")
print(context)

answer = qa.generate_answer(context, query)

print("\n=== FINAL ANSWER ===\n")
print(answer)