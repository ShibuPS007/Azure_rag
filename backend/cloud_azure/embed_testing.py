from chunking import TextChunker
from embeddings import EmbeddingService

chunker = TextChunker()
embedder = EmbeddingService()

text=["hi how are you.What is ai?"]

chunks = chunker.chunk_pages(text)

embedded_chunks = embedder.embed_chunks(chunks)

print("\nFirst embedded chunk:\n")

print(embedded_chunks[0]["page"])
print(len(embedded_chunks[0]["embedding"]))
# print(embedded_chunks[0]["content"])
# print(embedded_chunks[0]["embedding"])
