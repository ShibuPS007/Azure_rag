from pydantic import BaseModel, Field
from typing import List, Optional


class AgentState(BaseModel):
    query: str
    document_name: str
    docs: Optional[List[str]] = []
    answer: Optional[str] = None

    source: Optional[str] = None  
    score: Optional[float] = None
    decision: Optional[str] = None  
    retry_count: int = 0