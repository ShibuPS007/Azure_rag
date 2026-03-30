from .state import AgentState
from .tools import generate_answer,retrieve_docs,web_search
from backend.cloud_azure.qa_chain import QAChain

qa=QAChain()


def router_agent(state:AgentState):
    # query = state.query.lower()

    # for word in ["latest", "current", "news", "today","recent"]:
    #     if word in query:
    #         return {"source": "web"}

    # return {"source": "rag"}

    prompt = f"""
    Decide the best source:

    - "rag" → if query involves document understanding (e.g., "this doc",or any other words asked related to the document uploaded)
    - "web" → if query is ONLY about latest/current info
    - If query has BOTH → ALWAYS choose "rag" first

    Query: {state.query}

    Return ONLY one word: rag OR web
    """

    decision = qa.generate_answer("",prompt).lower()
    
    if "web" in decision:
        source = "web"
    else:
        source = "rag"

    return {"source": source}


def rag_agent(state:AgentState):
    
    docs,result=retrieve_docs(state.query,state.document_name)

    answer,context=generate_answer(docs,state.query)

    return {
        "docs": docs,
        "context": context,
        "answer": answer,
        "source": "rag",
        "sources": result
    }


def web_agent(state:AgentState):
    docs,sources= web_search(state.query)

    context="\n\n".join(docs)
    answer=qa.generate_answer(context,state.query)

    return {
        "answer": answer,
        "source": "web",
        "context":context,
        "sources":sources
    }

def evaluator_agent(state:AgentState):
    query=state.query
    answer=state.answer

    

    prompt = f"""
    Evaluate the answer quality.

    Query: {query}
    Answer: {answer}

    Step 1: Identify how many parts the query has.
    Step 2: Identify the intent of each part.
    Step 3: Check if ALL parts are answered.

    CHECK:
        - If query includes "recent", "latest", "new", or "current trends":
        → answer MUST include general knowledge, not just document content
        - If answer only uses document info for such parts → mark as incomplete

    IMPORTANT:
    - Check if ALL parts of the query are answered
    - If any part is missing → DO NOT accept
    - If partial → decision = combine
    - If wrong → decision = fallback
    - Only if ALL parts are answered → "accept"

    Score from 0 to 1 based on:
        - relevance
        - completeness (Very  Important)
        - correctness

    SCORING:
        - Missing part → max score 0.6
        - Wrong interpretation → max score 0.6
        - Fully correct → 0.8+

    Also return only an single word:
    decision: accept / combine / fallback
    
    Format:
    score: <number>
    decision: <value>
    
    Example format:
    score: 0.85
    decision: accept
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



def hybrid_agent(state:AgentState):

    if state.source=="rag":
        web_docs,web_source = web_search(state.query)

        web_context="\n\n".join(web_docs)

        
        prompt = f"""
        Combine the following two answers into one clear, non-redundant response.

        Query:
        {state.query}

        Document Answer:
        {state.answer}

        Web Context:
        {web_context}

        Instructions:
        - Merge both sources
        - Remove repetition
        - Keep it concise but complete
        """
        final_answer=qa.generate_answer("",prompt)
        return {
            "answer": final_answer,
            "source": "hybrid",
            "sources":web_source
        }
    elif state.source=="web":
        docs,result=retrieve_docs(state.query,state.document_name)
        rag_answer,context=generate_answer(docs,state.query)
        prompt = f"""
        Combine the following two answers into one clear, non-redundant response.

        Query:
        {state.query}

        Web Answer:
        {state.answer}

        Document Context:
        {context}

        Instructions:
        - Merge both sources
        - Remove repetition
        - Keep it concise but complete
        """
        final_result=qa.generate_answer("",prompt)

        return{
            "answer":final_result,
            "source":"hybrid",
        }
    else:
        return{
            "answer":state.answer,
            "source":state.source
        }





