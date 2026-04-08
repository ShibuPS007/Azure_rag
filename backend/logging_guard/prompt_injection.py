def detect_prompt_injection(query: str):
    patterns = [
        "ignore previous instructions",
        "act as system",
        "jailbreak",
        "bypass"
    ]
    return any(p in query.lower() for p in patterns)