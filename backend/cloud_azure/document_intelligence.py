import os
from azure.ai.formrecognizer import DocumentAnalysisClient

from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()


class DocumentIntelligenceService:

    def __init__(self):
        endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
        key=os.getenv("DOCUMENT_INTELLIGENCE_KEY")

        self.client=DocumentAnalysisClient(endpoint=endpoint,credential=AzureKeyCredential(key))

    def extract_text_from_pdf(self,pdf_bytes):

        # with open(pdf_path,"rb") as f:
        #     poller=self.client.begin_analyze_document("prebuilt-layout",document=f)

        poller=self.client.begin_analyze_document("prebuilt-layout",document=pdf_bytes)

        result=poller.result()

        # return result
    
        # extracted_text=""

        # for page in result.pages:
        #     for line in page.lines:
        #         extracted_text+=line.content + "\n"

        # return extracted_text


        pages=[]

        for page in result.pages:
            page_text=""

            for line in page.lines:
                page_text+=line.content +"\n"

            pages.append(page_text)

        return pages