import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class QAChain:

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_CHAT_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-02-15-preview"
        )

        self.model = os.getenv("AZURE_OPENAI_CHAT_MODEL")

    def build_prompt(self, context, question):

        return f"""
            You are an AI assistant answering questions based on a document.Answer ONLY from the given context.Do not make up your own answers.
  
            Context:
            {context}

            Question:
            {question}

            Answer:
            """

    def generate_answer(self, context, question):

        prompt = self.build_prompt(context, question)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        
        return response.choices[0].message.content