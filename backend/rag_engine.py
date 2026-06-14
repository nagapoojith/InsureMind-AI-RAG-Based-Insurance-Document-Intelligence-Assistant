import os
import chromadb

backend_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = r"C:\Users\DELL\OneDrive\Documents\RAG PROJECT\Insurance Rag\chroma_db"
embedding_model = None
reranker = None
llm = None
vector_db = None
models_ready = False


def initialize_models():
    global embedding_model, reranker, llm, vector_db, models_ready

    if models_ready:
        return

    print("\n" + "=" * 100)
    print("🛡️ InsureMind AI Boot Sequence Initiated...")
    print("📂 Connecting to Insurance Knowledge Vault...")
    print("🧠 Loading Semantic Intelligence Engine...")
    print("🎯 Activating Precision Evidence Ranking...")
    print("🤖 Starting Conversational Reasoning Core...")

    from langchain_huggingface import HuggingFaceEmbeddings
    from sentence_transformers import CrossEncoder
    from langchain_ollama import OllamaLLM
    from langchain_chroma import Chroma

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    reranker = CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )

    llm = OllamaLLM(
        model="llama3.2:3b",
        temperature=0,
        num_predict=220,
        top_k=20,
        top_p=0.9
    )

    client = chromadb.PersistentClient(path=DB_PATH)

    vector_db = Chroma(
        client=client,
        embedding_function=embedding_model
    )

    models_ready = True

    print("✅ All AI Systems Online")
    print("=" * 100)


def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


def rerank_results(query, docs):
    pairs = [
        (query, clean_text(doc.page_content[:700]))
        for doc in docs
    ]

    scores = reranker.predict(pairs)

    scored_docs = list(zip(scores, docs))
    scored_docs.sort(key=lambda x: x[0], reverse=True)

    return [doc for score, doc in scored_docs[:2]]


def generate_answer(query, docs):
    context = "\n\n".join([
        f"""
Document: {os.path.basename(doc.metadata.get('source', 'Unknown'))}
Page: {doc.metadata.get('page', 'Unknown')}

Content:
{clean_text(doc.page_content[:900])}
"""
        for doc in docs
    ])

    prompt = f"""
You are InsureMind AI, a professional insurance document assistant.

STRICT RULES:
1. Answer ONLY using provided insurance documents.
2. NEVER use outside knowledge.
3. NEVER guess.
4. If answer is not clearly found, reply EXACTLY:
Information not found in provided documents.
5. Convert broken PDF text into proper readable English.
6. Remove weird PDF numbering unless necessary.
7. If multiple conditions, benefits, exclusions, or comparisons exist, use bullet points.
8. Be clear, professional, and user-friendly.

Insurance Documents:
{context}

User Question:
{query}

Answer:
"""

    return llm.invoke(prompt).strip()


def ask_question(query):
    initialize_models()

    print(f"\n🔍 User Query: {query}")
    print("📄 Retrieving relevant insurance evidence...")

    retrieved_docs = vector_db.similarity_search(query, k=8)

    if not retrieved_docs:
        print("❌ No relevant evidence found.")
        return {
            "found": False,
            "answer": "Information not found in provided documents."
        }

    print("🎯 Ranking evidence relevance...")
    best_docs = rerank_results(query, retrieved_docs)

    print("🤖 Generating verified response...")
    answer = generate_answer(query, best_docs)

    if "Information not found in provided documents." in answer:
        print("❌ Verified result: not found.")
        return {
            "found": False,
            "answer": "Information not found in provided documents."
        }

    sources = []
    excerpts = []

    for doc in best_docs:
        sources.append({
            "document": os.path.basename(
                doc.metadata.get("source", "Unknown")
            ),
            "page": doc.metadata.get("page", "Unknown")
        })

        excerpts.append(
            clean_text(doc.page_content[:350])
        )

    print("✅ Response delivered.")

    return {
        "found": True,
        "answer": answer,
        "sources": sources,
        "excerpts": excerpts
    }