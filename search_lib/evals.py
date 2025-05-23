__all__ = ["average_precision_evaluator", "r_precision_evaluator", "nrbp_evaluator", "recall_evaluator"]

def average_precision_evaluator(expected, output, k=200):
    """
    Calculate the average precision at k for the given expected and output documents.
    Average precision is the average of precision values at positions where relevant documents are found.
    """
    gold_standard_docs = {
        str(document["anki_id"])  
        for document in expected["documents"]
        if document["rating"] == 1.0
    }
    
    total_relevant = len(gold_standard_docs)
    if total_relevant == 0:
        return 0.0
    
    retrieved_ids = [str(doc["anki_id"]) for doc in output["documents"][:k]]
    
    num_relevant = 0
    precision_scores = []
    seen = set()    
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if str(doc_id) in gold_standard_docs and doc_id not in seen:
            seen.add(doc_id)
            num_relevant += 1
            precision_scores.append(num_relevant / rank)
    
    # Divide by total number of relevant documents
    return sum(precision_scores) / total_relevant if precision_scores else 0.0

def r_precision_evaluator(expected, output):
    """
    Calculate the r-precision for the given expected and output documents.
    R-precision is the precision at R, where R is the number of relevant documents.
    """
    gold_standard_docs = {
        str(document["anki_id"])  # Use ankihub_id from reference docs
        for document in expected["documents"]
        if document["rating"] == 1.0
    }
    
    num_gold_docs = len(gold_standard_docs)
    if num_gold_docs == 0:
        return 0.0
    
    # Get the top R retrieved documents
    retrieved_ids = [str(doc["anki_id"]) for doc in output["documents"][:num_gold_docs]]
    
    # Count relevant documents in the top R
    relevant_count = sum(1 for doc_id in retrieved_ids if str(doc_id) in gold_standard_docs)
    
    # Calculate precision
    precision = relevant_count / num_gold_docs if num_gold_docs > 0 else 0.0
    
    return precision

def nrbp_evaluator(expected, output, p=0.8):
    gold_standard_docs = {
        str(document["anki_id"])  # Use ankihub_id from reference docs
        for document in expected["documents"]
        if document["rating"] == 1.0
    }

    retrieved_ids = [str(doc["anki_id"]) for doc in output["documents"]]
    rbp_score, discount, relevant_count = 0.0, 1.0, 0    
    normalizer = (1 - p) / (1 - p**len(gold_standard_docs)) if p < 1 else 1/len(gold_standard_docs)
    
    for doc_id in retrieved_ids:
        if str(doc_id) in gold_standard_docs:  # Convert to string to ensure comparison works
            rbp_score += discount
            relevant_count += 1
        discount *= p
    
    nrbp_score = rbp_score * normalizer
    
    return nrbp_score

def recall_evaluator(expected, output, k=200):
    """Calculate recall at k for the given expected and output documents."""
    gold_standard_docs = {
        str(document["anki_id"])
        for document in expected["documents"]
        if document["rating"] == 1.0
    }
    
    total_relevant = len(gold_standard_docs)
    if total_relevant == 0:
        return 0.0
    
    retrieved_ids = [str(doc["anki_id"]) for doc in output["documents"][:k]]
    relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in gold_standard_docs)
    
    return relevant_retrieved / total_relevant