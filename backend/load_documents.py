import os
from langchain_community.document_loaders import PyPDFLoader

DATA_PATH = r"C:\Users\DELL\Documents\RAG PROJECT\INSURANCE DATA"

all_documents = []

for root, dirs, files in os.walk(DATA_PATH):
    for file in files:
        if file.endswith(".pdf"):
            pdf_path = os.path.join(root, file)
            print("Loading:", pdf_path)

            loader = PyPDFLoader(pdf_path)
            docs = loader.load()

            all_documents.extend(docs)

print("Total pages loaded:", len(all_documents))