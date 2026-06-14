import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from sentence_transformers import CrossEncoder

# ================= CONFIG =================
DATA_PATH = r"C:\Users\DELL\Documents\RAG PROJECT\INSURANCE DATA"
DB_PATH = r"C:\Users\DELL\Documents\RAG PROJECT\Insurance Rag\chroma_db"

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_MODEL = "llama3.2:3b"

# ================= STARTUP =================
print("\n" + "=" * 100)
print("🛡️ InsureMind - Intelligent Insurance Document Assistant")
print("=" * 100)
print("⏳ Initializing optimized document intelligence system...")

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

reranker = CrossEncoder(RERANKER_MODEL)

llm = OllamaLLM(
    model=LLM_MODEL,
    temperature=0,
    num_predict=220,
    top_k=20,
    top_p=0.9
)

print("✅ Core systems ready.")
print("=" * 100)

# ================= HELPERS =================
def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

# ================= LOAD DOCS =================
def load_documents():
    all_documents = []

    for root, dirs, files in os.walk(DATA_PATH):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                print(f"📄 Loading: {file}")

                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                all_documents.extend(docs)

    print(f"\n✅ Total pages loaded: {len(all_documents)}")
    return all_documents

# ================= CHUNKING =================
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=850,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)
    print(f"✅ Total chunks created: {len(chunks)}")
    return chunks

# ================= VECTOR DB =================
def build_vector_db(chunks):
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH
    )

    print("✅ Vector database created successfully.")
    return vector_db

def load_vector_db():
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )

# ================= RERANK =================
def rerank_results(query, docs):
    pairs = [(query, clean_text(doc.page_content[:700])) for doc in docs]
    scores = reranker.predict(pairs)

    scored_docs = list(zip(scores, docs))
    scored_docs.sort(key=lambda x: x[0], reverse=True)

    return [doc for score, doc in scored_docs[:2]]

# ================= ANSWER =================
def generate_answer(query, docs):
    context = "\n\n".join(
        [
            f"Document: {os.path.basename(doc.metadata.get('source', 'Unknown'))} | Page: {doc.metadata.get('page', 'Unknown')}\n{clean_text(doc.page_content[:800])}"
            for doc in docs
        ]
    )

    prompt = f"""
You are a professional insurance assistant.

STRICT RULES:
1. Answer ONLY from provided insurance content.
2. Do NOT guess.
3. Do NOT invent policy information.
4. If answer is not clearly found, respond EXACTLY:
Information not found in provided documents.
5. Use simple professional English.
6. If multiple conditions, exclusions, benefits, or steps exist, use bullet points.
7. Ignore broken PDF formatting and reconstruct readable text faithfully.
8. No outside knowledge.

Insurance Content:
{context}

Question:
{query}

Answer:
"""

    return llm.invoke(prompt).strip()

# ================= MAIN =================
def main():
    if not os.path.exists(DB_PATH):
        print("\n📂 No database found.")
        print("📚 Building optimized insurance knowledge base...\n")

        docs = load_documents()
        chunks = chunk_documents(docs)
        vector_db = build_vector_db(chunks)

    else:
        print("\n📂 Loading existing database...")
        vector_db = load_vector_db()
        print("✅ Database loaded successfully.")

    while True:
        query = input("\n💬 Ask your insurance question (type 'exit'): ")

        if query.lower() == "exit":
            print("\n👋 InsureMind session ended.")
            break

        print("\n🔍 Searching policy documents...")
        retrieved_docs = vector_db.similarity_search(query, k=8)

        if not retrieved_docs:
            print("\n" + "=" * 100)
            print("📌 VERIFIED ANSWER:\n")
            print("Information not found in provided documents.")
            print("=" * 100)
            continue

        print("📌 Ranking best evidence...")
        best_docs = rerank_results(query, retrieved_docs)

        print("📝 Generating response...")
        answer = generate_answer(query, best_docs)

        if "Information not found in provided documents." in answer :
            print("\n" + "=" * 100)
            print("📌 VERIFIED ANSWER:\n")
            print("Information not found in provided documents.")
            print("=" * 100)
            continue

        print("\n" + "=" * 100)
        print("📌 VERIFIED ANSWER:\n")
        print(answer)

        print("\n📄 SOURCE DETAILS:")
        for i, doc in enumerate(best_docs, 1):
            source_file = os.path.basename(doc.metadata.get("source", "Unknown"))
            page_no = doc.metadata.get("page", "Unknown")
            print(f"{i}. {source_file} | Page {page_no}")

        print("\n🧾 REFERENCE EXCERPT:")
        for i, doc in enumerate(best_docs, 1):
            snippet = clean_text(doc.page_content[:300])
            print(f"\n{i}. {snippet}")

        print("=" * 100)

if __name__ == "__main__":
    main()