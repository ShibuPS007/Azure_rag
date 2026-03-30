from backend.cloud_azure.blob_storage import BlobStorageService
from backend.cloud_azure.document_intelligence import DocumentIntelligenceService
from backend.cloud_azure.tokens import TokenCounter
from backend.cloud_azure.chunking import TextChunker
from backend.cloud_azure.embeddings import EmbeddingService
from backend.cloud_azure.indexer import AzureSearchIndexer


def process_document(pdf_bytes, doc_name):# used in main

    indexer = AzureSearchIndexer()
    embedder = EmbeddingService()
    chunker = TextChunker()
    token_count = TokenCounter()
    blob = BlobStorageService()
    doc_service = DocumentIntelligenceService()

    blob_name = doc_name

    url = blob.upload_pdf(pdf_bytes, blob_name)
    print("PDF uploaded:", url)

    text = doc_service.extract_text_from_pdf(pdf_bytes)

    print("\nExtracted text preview:\n", text[:100])

    token = token_count.get_token_statistics(text)
    print("Token stats:", token)

    print("-----------------------------------------------------")

    chunks = chunker.chunk_pages(text)
    print(f"Total chunks: {len(chunks)}")

    embedded_chunks = embedder.embed_chunks(chunks)
    print("Embedding done")

    indexer.upload_embeddings(embedded_chunks, doc_name)
    print("Indexing completed")

    return doc_name