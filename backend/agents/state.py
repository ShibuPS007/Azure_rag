from pydantic import BaseModel, Field
from typing import List, Optional


class AgentState(BaseModel):
    query: str
    document_name: str
    docs: Optional[List[str]] = []
    context:Optional[str]=None
    answer: Optional[str] = None

    analysis:Optional[list]=None
    source: Optional[str] = None  
    score: Optional[float] = None
    decision: Optional[str] = None  
    retry_count: int = 0