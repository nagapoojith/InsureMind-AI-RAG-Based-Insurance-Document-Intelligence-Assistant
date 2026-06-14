import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

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

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(all_documents)

print("Total chunks:", len(chunks))

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector = embedding_model.embed_query(chunks[0].page_content)

print("Embedding vector length:", len(vector))