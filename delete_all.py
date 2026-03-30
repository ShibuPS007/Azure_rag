from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

endpoint = ""
index_name = ""


client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

while True:
    results = list(client.search("*", select=["id"], top=1000))
    
    if not results:
        break
    
    docs = [{"id": doc["id"]} for doc in results]
    client.delete_documents(documents=docs)
    
    print(f"Deleted batch of {len(docs)} docs")

print("✅ All documents + embeddings deleted")