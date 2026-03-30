from ingestion.embeddings import get_embedding_model
from ingestion.indexer import connect_vector_store

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


embedding_model = get_embedding_model()

vector_store = connect_vector_store(embedding_model)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant.

Use ONLY the context below to answer the question.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
""")

def answer_question(query: str):

    docs = retriever.invoke(query)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": query
    })

    print("\nAnswer:\n")
    print(response.content)

    # print("\nSources:\n")
    # for i, doc in enumerate(docs):
    #     print(f"Source {i+1} | Page:", doc.metadata.get("page"))


if __name__ == "__main__":

    while True:

        query = input("\nAsk a question (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        answer_question(query)