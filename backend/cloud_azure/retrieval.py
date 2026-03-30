from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()


class AzureRetriever:

    def __init__(self):
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        key = os.getenv("AZURE_SEARCH_KEY")
        index_name = os.getenv("AZURE_SEARCH_INDEX")

        self.client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key)
        )

    def search(self, query_embedding, top_k=3, document_name=None):

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=5,
            fields="contentVector"
        )

        filter_query = None
        if document_name:
            filter_query = f"document eq '{document_name}'"

        results = self.client.search(
            search_text="*",
            vector_queries=[vector_query],
            filter=filter_query,
            top=top_k
        )

        chunks = []

        for result in results:
            chunks.append({
                "content": result["content"],
                "page": result["page"],
                "document": result["document"],
                "score": result["@search.score"]
            })

        return chunks