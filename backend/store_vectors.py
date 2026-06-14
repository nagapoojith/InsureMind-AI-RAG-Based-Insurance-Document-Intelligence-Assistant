import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

DATA_PATH = r"C:\Users\DELL\Documents\RAG PROJECT\INSURANCE DATA"
DB_PATH = "./chroma_db"

all_documents = []

# Load PDFs
for root, dirs, files in os.walk(DATA_PATH):
    for file in files:
        if file.endswith(".pdf"):
            pdf_path = os.path.join(root, file)
            print("Loading:", pdf_path)

            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            all_documents.extend(docs)

# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(all_documents)

print("Total chunks:", len(chunks))

# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Store in ChromaDB
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=DB_PATH
)

print("Vector database created successfully!")