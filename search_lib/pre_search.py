from pydantic import BaseModel
from openai import OpenAI
import instructor
import os
from typing import List
from .prompt import QUERY_DECOMPOSITION_PROMPT
from typing import BinaryIO
from .load_data import get_s3_client
import os,re,io, requests
from .prompt import PDF_PROCESSING_PROMPT, KEYWORD_EXPANSION_PROMPT
from urllib.parse import urlparse
from google.generativeai import GenerativeModel
import google.generativeai as genai

def decompose_query(qry:tuple, model="gpt-3.5-turbo", verbose:bool=False)->list:
    class DecomposedDocument(BaseModel):
        queries: List[str]
        expanded_terms: List[str]
            
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

def keyword_expansion(qry: str, model="gpt-3.5-turbo") -> str:
    """Expand a medical query with related terms and synonyms"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": KEYWORD_EXPANSION_PROMPT.format(qry=qry)}],
        temperature=0.3,
        max_tokens=100
    )

    expanded_query = response.choices[0].message.content.strip()

    # If we just got back the original query or something very similar, try again with more explicit instructions
    if expanded_query.lower() == qry.lower() or len(expanded_query.split()) <= len(qry.split()):
        prompt += "\nImportant: Add at least 3-5 additional related medical terms beyond the original query."
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        expanded_query = response.choices[0].message.content.strip()

    return expanded_query

def extract_s3_key_from_ankihub_url(url: str) -> str | None:
    "Check if URL is an AnkiHub file URL and extract the S3 key if it is."
    ankihub_pattern = r"https://app\.ankihub\.net/ai/file-search/input-file/(ai-files/.+)"
    match = re.match(ankihub_pattern, url)
    if match: return match.group(1).rstrip("/")

def convert_to_direct_download_url(url: str
                                  ) -> str: # A direct download URL if conversion is possible, otherwise the original URL
    "Convert sharing URLs to direct download URLs when possible."
    if "drive.google.com" in url and "/file/d/" in url:
        match = re.search(r"/file/d/([^/]+)", url)
        if match:
            file_id = match.group(1)
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            return direct_url
    return url

def get_file_from_prod_s3(key: str) -> BinaryIO:
    "Get a file stream from an S3 bucket."
    file_stream = io.BytesIO()
    s3_client = get_s3_client()
    s3_client.download_fileobj('ankihub', key, file_stream)
    file_stream.seek(0)
    return file_stream

def get_file_from_url(url: str, timeout: int = 30) -> BinaryIO:
    "Download a file from a URL."
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()
    file_stream = io.BytesIO(response.content)
    return file_stream

def process_pdf(url:str, model_name="gemini-1.5-pro", verbose:bool=False)->str:
    netloc = urlparse(url).netloc
    if netloc == 'app.ankihub.net':
        _url = extract_s3_key_from_ankihub_url(url)
        _file = get_file_from_prod_s3(_url)
    elif netloc == 'drive.google.com':
        _url = convert_to_direct_download_url(url)
        _file = get_file_from_url(_url)
    else:
        raise ValueError(f"Unsupported URL: {url}")
    _file.seek(0)
    pdf_bytes = _file.read()
    model = GenerativeModel(model_name)
    response = model.generate_content([PDF_PROCESSING_PROMPT, {"mime_type": "application/pdf", "data": pdf_bytes}])
    return response.text

