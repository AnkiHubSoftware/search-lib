from setuptools import setup, find_packages

setup(
    name="search_lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "python-dotenv",
    ],
    author="AnkiHub",
    description="A library for AnkiHub search functionality",
    python_requires=">=3.7",
)