import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import uuid
import re
load_dotenv()

class AzureSearchIndexer:
    def __init__(self):
    
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT")
        key=os.getenv("AZURE_SEARCH_KEY")
        index_name=os.getenv("AZURE_SEARCH_INDEX")


        self.client=SearchClient(endpoint=endpoint,index_name=index_name,credential=AzureKeyCredential(key))

    def upload_embeddings(self,embedded_chunks,document_name):

        docs=[]

        for i,chunk in enumerate(embedded_chunks):
            
            doc_id=f"{document_name}_p{chunk['page']}_c{i}"
            docs.append({
                "id": doc_id,
                "content": chunk["content"],
                "page": chunk["page"],
                "document": document_name,
                "contentVector": chunk["embedding"]
            })


        self.client.upload_documents(docs)

        print(f"{len(docs)} documents indexed successfully")


    def document_exists(self, document_name):

        results = self.client.search(
            search_text="*",
            filter=f"document eq '{document_name}'",
            top=1
        )

        return len(list(results)) > 0
    
    

    def sanitize_key(self,key: str) -> str:
        # replace invalid chars with underscore
        return re.sub(r'[^a-zA-Z0-9_\-=]', '_', key)