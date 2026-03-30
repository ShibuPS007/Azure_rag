from backend.cloud_azure.retrieval import AzureRetriever
from .state import AgentState
from backend.cloud_azure.embeddings import EmbeddingService
from backend.cloud_azure.qa_chain import QAChain
from dotenv import load_dotenv
import os
from langchain_tavily import TavilySearch



load_dotenv()

qa=QAChain()
retriever=AzureRetriever()
embedder=EmbeddingService()


def retrieve_docs(query:str,document_name:str):
    print("🔍 Query:", query)#
    query_embedding=embedder.embed_query(query)

    results=retriever.search(
        query_embedding, 
        top_k=3,
        document_name=document_name)
    
    print("📦 Raw Results:", results)#

    docs=[r["content"] for r in results]
    print("📄 Extracted Docs:", docs)#
    return docs, results

def generate_answer(docs:list,query:str):
    context="\n\n".join(docs)
    answer=qa.generate_answer(context,query)
    return answer, context


def web_search(query: str):
    tavily = TavilySearch(max_results=3,api_key=os.getenv("TAVILY_API_KEY"))

    # key=os.getenv("TAVILY_API_KEY")

    results=tavily.invoke(query)

    docs=[]
    sources=[]

    for r in results["results"]:
        docs.append(r.get("content"))
        sources.append(r.get("url"))
    return docs,sources