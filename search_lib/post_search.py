import cohere
import os

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def cohere_rerank(query, notes, top_k=5, **kwargs):
    "Rerank notes using Cohere's Rerank API."
    return co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[r['content'] for r in notes],
        return_documents=True,
        **kwargs
    )

def llm_rerank(query, notes):
    " Use an LLM to rerank notes.  Slow but can be powerful method for fine-tuning results."
    raise NotImplementedError("LLM reranking is not implemented yet.")

    # Class for structured output
    class RelevanceCategory:
        "Stores a boolean that indicates where a result from a search is relevant or not to the user query"
        def __init__(self, is_relevant:bool):
            self.is_relevant = is_relevant
