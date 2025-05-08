import io
import sqlite3
import boto3, os
import json
from pathlib import Path

__all__ = ["get_notes", "download_sqlite_file"]

def get_s3_client():  
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_S3_REGION_NAME"),
    )
    return client

def download_sqlite_file(deck_name:str="AnKing Step Deck", replace:bool=False)->Path:
    """Download the SQLite file from S3"""
    print(f"Downloading SQLite file for deck: {deck_name}")
    s3_client = get_s3_client()
    file_name = f"{deck_name}.sqlite"
    local_path = Path(file_name)

    if local_path.exists(): 
        if replace: local_path.unlink()
        else: return local_path

    # Download to memory buffer first
    file_buffer = io.BytesIO()
    s3_client.download_fileobj("ankihub", file_name, file_buffer)
    file_buffer.seek(0)

    # Write buffer contents to file
    with open(local_path, "wb") as f:
        f.write(file_buffer.getvalue())
    return local_path

def get_notes(db_path:Path)->list:
    """Get the notes from the SQLite file"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, fields, corpus, tags_cache FROM notes")
    
    notes = []
    for row in cursor.fetchall():
        note_id, fields_json, corpus, tags_json = row
        try:
            fields = json.loads(fields_json)
            content = " ".join([f.get("value", "") for f in fields if isinstance(f, dict)])
        except:
            content = corpus
        if not content: continue
            
        # Parse tags
        try: tags = json.loads(tags_json) if tags_json else []
        except: tags = []
            
        notes.append({"id": note_id, "content": content, "tags": tags})
    
    conn.close()
    print(f"Extracted {len(notes)} notes with content")
    return notes