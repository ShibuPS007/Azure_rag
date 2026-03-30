import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key="AIzaSyCTvPbcq-6tnYbnV5JkWxGaNKF4g6YhdFM"
    )