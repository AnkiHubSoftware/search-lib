import cohere
import os
from pydantic import BaseModel, Field
import instructor 
import google.generativeai as genai

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

def llm_rerank(query, notes, limit=None, model_name="gemini-1.5-flash"):
    """Use an LLM to rerank notes based on relevance to the query."""
    class RelevanceScore(BaseModel):
        score: float = Field(description="Relevance score from 0-1")
    
    # Initialize the model
    model = genai.GenerativeModel(model_name)
    client = instructor.from_generative_model(model, mode=instructor.Mode.TOOLS)
    
    def process_note(note):
        text = note.get('corpus') or note.get('note')
        if not text: return None
        
        resp = client.chat.completions.create(
            response_model=RelevanceScore,
            messages=[
                {"role": "user", "content": f"Query: {query}\n\nDocument: {text}\n\nRate how relevant this document is to the query from 0.0 (not relevant) to 1.0 (highly relevant). Just return the score."}
            ]
        )
        note_copy = note.copy()
        note_copy["relevance_score"] = resp.score
        return note_copy
    
    results = [r for r in parallel(process_note, notes) if r is not None]
    results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    if limit: return results[:limit]
    return results
