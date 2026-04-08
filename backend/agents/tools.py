from backend.cloud_azure.retrieval import AzureRetriever
from .state import AgentState
from backend.cloud_azure.embeddings import EmbeddingService
from backend.cloud_azure.qa_chain import QAChain
from dotenv import load_dotenv
import os
from langchain_tavily import TavilySearch
import json



load_dotenv()

qa=QAChain()
retriever=AzureRetriever()
embedder=EmbeddingService()


def retrieve_docs(query:str,document_name:str):
    print("🔍 Query:", query)#
    query_embedding=embedder.embed_query(query)

    results=retriever.search(
        query,
        query_embedding, 
        top_k=3,
        document_name=document_name)
    
    print("==== RETRIEVED CHUNKS ====")

    for r in results:
        print("CONTENT:", r["content"][:200])
        print("SCORE:", r["score"])
        print("----------------------")

    docs = [r["content"] for r in results]

    return docs, results

def generate_answer(docs: list, query: str):
    context = "\n\n".join(docs)

    prompt = f"""
    You are a secure AI assistant.

    Answer the question using ONLY the provided context.

    STRICT RULES:
    - Do NOT reveal full document content
    - Do NOT expose sensitive/confidential information (emails, numbers, IDs, etc.)
    - Only answer what is explicitly asked
    - If the question asks for sensitive or unrelated data → respond: "Not allowed"
    - If answer is not present → say: "Not enough information"
    - Do NOT hallucinate

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    answer = qa.generate_answer("", prompt)

    return answer, context


def web_search(query: str):
    tavily = TavilySearch(max_results=5,api_key=os.getenv("TAVILY_API_KEY"))

    # key=os.getenv("TAVILY_API_KEY")

    results=tavily.invoke(query)

    docs=[]
    sources=[]

    for r in results["results"]:
        docs.append(r.get("content"))
        sources.append(r.get("url"))
    return docs,sources

def analyze_query_llm(query, docs):
    context = "\n\n".join(docs)

    prompt = f"""
    Analyze the query with respect to the document.

    Query:
    {query}

    Document:
    {context}

    Tasks:
    1. Split the query into meaningful parts (NOT individual words)
    2. Each part must represent a complete question or intent

    Rules:
    - NEVER split into single words like "what", "is", "the"
    - Keep phrases intact (e.g., "what type of document is this")
    - Only split if there are multiple independent questions
        Example:
        "what is this doc and what is exponential value"
        → split into:
        1. "what is this doc"
        2. "what is exponential value"

    - Correct minor spelling mistakes before analysis (e.g., "ttype" → "type")

    - For each part, classify:
        - "relevant" → if the question can be answered using the document content (even indirectly or by summarizing)
        - "not_relevant" → if the question requires knowledge NOT present in the document

    Query: "what type of document is this"
    → relevant (because it can be inferred from the document content)

    Query: "what is exponential value"
    → not_relevant (not present in document)

    Query: "summarize this document"
    → relevant

    Return ONLY valid JSON.
    Do NOT include explanation.
    Do NOT include any text outside JSON.

    Format:
    [
    {{"part": "full phrase", "relevance": "relevant"}}
    ]
    """

    response = qa.generate_answer("", prompt)

    try:
        parsed = json.loads(response)
    except Exception as e:
        print("[JSON ERROR]", e)
        print("[RAW RESPONSE]", response)
        return []

    return parsed