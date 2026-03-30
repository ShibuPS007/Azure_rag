import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-02-15-preview"
        )

        self.model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")

    def create_embedding(self, text):

        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )

        return response.data[0].embedding


    def embed_chunks(self, chunks):

        embeddings = []

        for chunk in chunks:

            vector = self.create_embedding(chunk["content"])

            embeddings.append({
                "content": chunk["content"],
                "page": chunk["page"],
                "embedding": vector
            })

        return embeddings
    
    def embed_query(self, query: str):
        return self.create_embedding(query)