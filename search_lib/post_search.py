import cohere
import os

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def cohere_rerank(query, notes, top_k=5):
    "Rerank notes using Cohere's Rerank API."
    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=notes
    )
    return response.results