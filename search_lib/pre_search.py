from pydantic import BaseModel
from openai import OpenAI
import instructor
import os
from typing import List
from .prompt import QUERY_DECOMPOSITION_PROMPT

def decompose_query(qry:tuple, model="gpt-3.5-turbo", verbose:bool=False)->list:
    class DecomposedDocument(BaseModel):
        queries: List[str]
            
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    client = instructor.patch(client)
    prompt = QUERY_DECOMPOSITION_PROMPT.format(qry=qry)
    if verbose: 
        print(f"Decomposing query: {qry}")
        print(prompt)

    return client.chat.completions.create(
        model=model,
        response_model=DecomposedDocument,
        messages=[{"role": "user", "content": prompt}])