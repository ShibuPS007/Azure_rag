from blob_storage import BlobStorageService
from document_intelligence import DocumentIntelligenceService
import os
from tokens import TokenCounter
from chunking import TextChunker
from embeddings import EmbeddingService
from indexer import AzureSearchIndexer


indexer=AzureSearchIndexer()
embedder=EmbeddingService()
chunker=TextChunker()
token_count=TokenCounter()
blob = BlobStorageService()
doc_service=DocumentIntelligenceService()

file_path="ingestion/PS Shibu_Resume.pdf"




blob_name=os.path.basename(file_path)
doc_name=indexer.sanitize_key(blob_name)

if indexer.document_exists(doc_name):
    print("Document already indexed. Skipping...")
    exit()
else:
    url=blob.upload_pdf(file_path)
    print("PDF uploaded")
    print("File URL:", url)
    pdf_bytes=blob.download_pdf(blob_name)

    text=doc_service.extract_text_from_pdf(pdf_bytes)

    print("\nExtracted text:\n")
    print(text[:100])

    token=token_count.get_token_statistics(text)

    print(token)
    print("-----------------------------------------------------")

    chunks=chunker.chunk_pages(text)

    print("\nchunks:\n")

    for c in chunks:
        print(c["page"], ":",c["content"])

    embedded_chunks=embedder.embed_chunks(chunks)

    print("\nFirst embedded chunk:\n")

    print(embedded_chunks[0]["page"])
    print(embedded_chunks[0]["content"])
    print(len(embedded_chunks[0]["embedding"]))

        
    indexer.upload_embeddings(embedded_chunks, doc_name)


