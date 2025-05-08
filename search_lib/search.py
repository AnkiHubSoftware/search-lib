import bm25s
from pathlib import Path
import sqlite3
import numpy as np
import cohere
import os
from datetime import datetime
from tqdm import tqdm
from datetime import datetime

__all__ = ["dense_search", "sparse_search", "hybrid_search", "embed_cohere"]

def embed_cohere(docs:list, model:str="embed-english-v3.0", verbose:bool=False, input_type:str="search_query", batch_size:int=96)->np.ndarray:
    """Embed documents using Cohere API with batching and progress bar."""
    with cohere.Client(os.getenv("COHERE_API_KEY")) as co:
        if verbose: print(f"{datetime.now()} : Embedding {len(docs)} documents with {model}...")
        embeddings = []
        for i in tqdm(range(0, len(docs), batch_size), disable=not verbose):
            batch = docs[i:i + batch_size]
            batch_embeddings = co.embed(
                texts=batch,
                model=model,
                input_type=input_type
            ).embeddings
            embeddings.extend(batch_embeddings)
        return np.array(embeddings)

def dense_search(query:str, notes:list[dict], embeddings=None, top_k=5, verbose:bool=False):
    "Search for notes in the database using a query and cohere dense embeddings."
    if embeddings is None: embeddings = embed_cohere(notes, verbose=verbose, input_type='search_document')
    query_emb = embed_cohere([query], verbose=verbose, input_type='search_query')
    if verbose: print(f"{datetime.now()} : Searching...")

    # Reshape query embedding to match document embeddings
    query_emb = query_emb.reshape(-1)  # Flatten to 1D array

    # Compute cosine similarity
    sims = np.dot(embeddings, query_emb) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb))
    top_idxs = np.argsort(sims)[::-1][:top_k]

    return [{
        "id": notes[i]["id"],
        "content": notes[i]["content"],
        "similarity": float(sims[i]),
        "tags": notes[i]["tags"]
    } for i in top_idxs], embeddings

def tokenize_notes(notes, verbose:bool=False):
    "Tokenize all notes for BM25 search."
    if verbose: print(f"{datetime.now()} : Tokenizing {len(notes)} notes...")
    return bm25s.tokenize([note["content"] for note in notes])

def sparse_search(query, notes, notes_tokens=None, top_k=5, verbose:bool=False):
    "Search for notes using BM25 sparse retrieval."
    if verbose: print(f"{datetime.now()} : Indexing notes...")
    notes_content = [n['content'] for n in notes]
    # Create a mapping from content to note index for efficient lookup
    content_to_idx = {content: idx for idx, content in enumerate(notes_content)}

    retriever = bm25s.BM25(corpus=notes_content)
    if notes_tokens is None:
        notes_tokens = bm25s.tokenize(notes_content)
    retriever.index(notes_tokens)

    if verbose: print(f"{datetime.now()} : Searching...")
    query_tokens = bm25s.tokenize(query)
    docs, scores = retriever.retrieve(query_tokens, k=len(notes))

    bm25_scores = {}
    for idx, doc_id in enumerate(docs[0]):
        doc_id = str(doc_id) if isinstance(doc_id, np.str_) else doc_id
        if doc_id in content_to_idx:
            note_idx = content_to_idx[doc_id]
            bm25_scores[note_idx] = float(scores[0, idx])

    max_score = max(bm25_scores.values()) if bm25_scores else 1
    normalized_scores = {i: score/max_score for i, score in bm25_scores.items()}

    # Get top k results
    top_idxs = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return [{
        "id": notes[i]["id"],
        "content": notes[i]["content"],
        "similarity": float(score),
        "tags": notes[i]["tags"]
    } for i, score in top_idxs]

def hybrid_search(query, notes, embeddings=None, top_k=5, dense_weight=0.7, sparse_weight=0.3):
    "Search for notes using a weighted combination of dense and sparse retrieval."
    dense_scores = {r["id"]: r["similarity"] for r in dense_search(query, notes, embeddings, top_k=len(notes))}
    sparse_scores = {r["id"]: r["similarity"] for r in sparse_search(query, notes, top_k=len(notes))}

    results = []
    for note in notes:
        if note["id"] in dense_scores and note["id"] in sparse_scores:
            score = (dense_weight * dense_scores[note["id"]] +
                    sparse_weight * sparse_scores[note["id"]])
            results.append({
                "id": note["id"],
                "content": note["content"],
                "similarity": score,
                "tags": note["tags"]
            })

    return sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
