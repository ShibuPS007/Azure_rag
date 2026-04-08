from .state import AgentState
from .tools import generate_answer,retrieve_docs,web_search,analyze_query_llm
from backend.cloud_azure.qa_chain import QAChain

qa=QAChain()


def router_agent(state:AgentState):
    # query = state.query.lower()

    # for word in ["latest", "current", "news", "today","recent"]:
    #     if word in query:
    #         return {"source": "web"}

    # return {"source": "rag"}

    # prompt = f"""
    # Decide the best source:

    # - "rag" → if query involves document understanding (e.g., "this doc",or any other words asked related to the document uploaded)
    # - "web" → if query is ONLY about latest/current info
    # - If query has BOTH → ALWAYS choose "rag" first

    # Query: {state.query}

    # Return ONLY one word: rag OR web
    # """

    # decision = qa.generate_answer("",prompt).lower()
    
    # if "web" in decision:
    #     source = "web"
    # else:
    #     source = "rag"

    return {"source": "rag"}


def rag_agent(state:AgentState):
    
    docs,result=retrieve_docs(state.query,state.document_name)

    answer,context=generate_answer(docs,state.query)
    analysis = analyze_query_llm(state.query, docs)
    return {
        "docs": docs,
        "context": context,
        "answer": answer,
        "source": "rag",
        "sources": result,
        "analysis":analysis
    }


def hybrid_agent(state: AgentState):

    
    analysis = state.analysis or []

    relevant_parts = [item["part"] for item in analysis
        if item.get("relevance", "").lower() == "relevant"
    ]

    print(f"[HYBRID ANALYSIS] {analysis}")

    if not relevant_parts:
        return {
            "answer": state.answer,
            "source": "rag"
        }

    refined_query = " AND ".join(relevant_parts)

    intent_prompt = f"""
    Classify the query type:

    Query: {refined_query}

    Options:
    - news
    - general
    - technical

    Return ONLY one word.
    """

    intent = qa.generate_answer("", intent_prompt).strip().lower()

    
    search_query = refined_query

    if intent == "news":
        search_query += " latest trends 2026"
    elif intent == "technical":
        search_query += " detailed explanation"

    
    web_docs, web_sources = web_search(search_query)


    filtered_docs = []
    for doc in web_docs:
        if doc and len(doc.split()) > 20:
            filtered_docs.append(" ".join(doc.split()[:100]))

    web_context = "\n\n".join(filtered_docs[:3])


    # if not web_context.strip():
    #     return {
    #         "answer": state.answer,
    #         "source": "rag"
    #     }

    prompt = f"""
    Improve the document-based answer using web context.

    Query:
    {refined_query}

    Document Answer:
    {state.answer}

    Web Context:
    {web_context}

    Instructions:
    - Keep document answer as the base
    - Use web info ONLY if it adds missing or recent details
    - Do NOT answer unrelated parts
    - Do NOT add external knowledge beyond web context
    - Do NOT hallucinate
    - Keep answer clean and structured
    """

    final_answer = qa.generate_answer("", prompt)

    return {
        "answer": final_answer,
        "source": "hybrid",
        "sources": web_sources
    }


def evaluator_agent(state:AgentState):
    print(f"[STATE ANALYSIS IN EVALUATOR] {state.analysis}")
    query=state.query
    answer=state.answer
    analysis = state.analysis

    analysis = state.analysis or []

    relevant_parts = [
        item["part"]
        for item in analysis
        if item.get("relevance", "").lower() == "relevant"
    ]

    all_parts = [item["part"] for item in analysis]

    print(f"[ANALYSIS] {analysis}")

    
    if len(relevant_parts) < len(all_parts):
        print("Unrelated query parts detected -> restricting evaluation")

        
        query_to_evaluate = " AND ".join(relevant_parts)

        if not query_to_evaluate:
            
            return {
                "score": 0.0,
                "decision": "accept",
                "retry_count": state.retry_count + 1
            }
    else:
        query_to_evaluate = query
    

    prompt = f"""
    Evaluate the answer quality.

    Query: {query_to_evaluate}
    Answer: {answer}

    Step 1: Identify how many parts the query has.
    Step 2: Identify the intent of each part.
    Step 3: Check if ALL parts are answered.

    CHECK:
        
        - If answer only uses document info for such parts → mark as incomplete

    IMPORTANT:
    - Check if ALL parts of the query are answered
    - If any part is missing - DO NOT accept
    - If partial -> decision = combine
    - If wrong -> decision = fallback
    - Only if ALL parts are answered → "accept"

    Score from 0 to 1 based on:
        - relevance
        - completeness (Very  Important)
        - correctness


    Also return only an single word:
    decision: accept / combine / fallback
    
    Format:
    score: <number>
    decision: <value>
    """

    
    result=qa.generate_answer("",prompt)

    score = None
    decision = None

    for line in result.splitlines():
        if "score:" in line.lower():
            try:  
                score = float(line.split(":")[1].strip())
            except:
                pass
        elif "decision" in line.lower():
            try:
                decision = line.split(":")[1].strip()
            except:
                pass

    retry_count = state.retry_count + 1 
    print(f"[EVALUATOR] Score: {score}, Decision: {decision},Retry: {retry_count}")
    if retry_count > 1: 
        return { "score": score, "decision": "accept", "retry_count": retry_count }
    
    
    return{
        "score":score,
        "decision":decision,
        "raw":result,
        "retry_count": retry_count
    }









