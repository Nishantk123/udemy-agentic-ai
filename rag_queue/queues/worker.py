from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
import os

load_dotenv()

openai_client = OpenAI()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

vector_db = QdrantVectorStore.from_existing_collection(embedding=embedding_model, url="http://localhost:6333", collection_name="learning_rag")

def process_query(query:str):
    print("Searching Chunks", query)
    search_results = vector_db.similarity_search(query=query, k=3)
    context = "\n\n\n".join([f"Page Content: {result.page_content} \nPage Number:{result.metadata['page_label']}\n File Location: {result.metadata['source']}"
                         for result in search_results])
    SYSTEM_PROMPT = f"""
        You are a helpful AI assistant who answers user quaeries based on the available context
        retrieved from a pdf along with page_context ans page_number.

        You should only answer the user based on the following context and navigate the user to open the right 
        page number to know more

        Context:
        {context}

    """
    response = openai_client.chat.completions.create(
        model= "gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )
    print(f"answer: {response.choices[0].message.content}")
    return response.choices[0].message.content
