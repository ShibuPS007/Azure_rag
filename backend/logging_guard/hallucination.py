from backend.cloud_azure.qa_chain import QAChain

qa = QAChain()

def detect_hallucination(query, context, answer):

    prompt = f"""
    Check if the answer is fully supported by the given context.

    Query:
    {query}

    Context:
    {context}

    Answer:
    {answer}

    Rules:
    - If answer contains info NOT in context → hallucination = yes
    - If fully supported → hallucination = no

    Return ONLY:
    yes or no
    """

    result = qa.generate_answer("", prompt).strip().lower()

    return result == "yes"