from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    def __init__(self):
        self.splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=150)

    def chunk_pages(self,pages):

        chunks=[]

        for page_num,page_text in enumerate(pages, start=1):
            page_chunk=self.splitter.split_text(page_text)

            for chunk in page_chunk:
                chunks.append({"content":chunk,"page":page_num})


        return chunks