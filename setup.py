from setuptools import setup, find_packages

setup(
    name="search_lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Core dependencies
        "boto3",
        "python-dotenv",
        "pydantic",
        "numpy",
        "tqdm",
        
        # Search and embeddings
        "cohere",
        "bm25s",
        "weaviate-client",
        
        # LLM and AI
        "openai",
        "google-generativeai",
        "instructor",
        
        # HTTP and file handling
        "requests",
    ],
    author="AnkiHub",
    description="A library for AnkiHub search functionality",
    python_requires=">=3.7",
)