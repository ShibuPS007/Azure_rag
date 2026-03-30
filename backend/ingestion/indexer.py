import os
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()


def create_vector_store(chunks, embedding_model):

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")

    # get embedding dimension dynamically
    dimension = len(embedding_model.embed_query("test"))

    # check if index exists
    existing_indexes = [index.name for index in pc.list_indexes()]

    if index_name not in existing_indexes:

        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        # wait until index is ready
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)
    # clear old vectors
    index_stats = index.describe_index_stats()

    if index_stats["total_vector_count"] > 0:
        index.delete(delete_all=True)

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embedding_model
    )

    vector_store.add_documents(chunks)

    return vector_store


def connect_vector_store(embedding_model):

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")

    index = pc.Index(index_name)

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embedding_model
    )

    return vector_store
