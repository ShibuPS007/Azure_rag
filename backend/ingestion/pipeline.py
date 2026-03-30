from document_ai import load_pdf
from chunking import split_documents
from embeddings import get_embedding_model
from indexer import create_vector_store
from dotenv import load_dotenv
import os

load_dotenv()

print("Loading PDF...")
docs = load_pdf("attention-is-all-you-need-Paper.pdf")
print("Pages loaded:", len(docs))

print("Splitting documents...")
chunks = split_documents(docs)
print("Chunks created:", len(chunks))

print("Loading embedding model...")
embedding_model = get_embedding_model()


print("Creating vector store...")
vector_store = create_vector_store(chunks, embedding_model)

print("Vectors stored in Pinecone!")
