from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os
load_dotenv()

key=os.getenv("TAVILY_API_KEY")
tavily = TavilySearch(
    max_results=3,
    topic="general"   # can be "news", "finance"
)
results = tavily.invoke("latest AI news")

docs=[]
source=[]

for r in results["results"]:
    docs.append(r.get("content"))
    source.append(r.get("url"))

print(docs)