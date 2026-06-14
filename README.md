InsureMind AI – RAG-Based Insurance Document Intelligence Assistant

I successfully built InsureMind – an AI-Powered Insurance Document Intelligence Assistant that can understand insurance policy documents and answer user questions with accurate, document-backed responses.

Instead of giving generic AI answers, InsureMind uses Retrieval-Augmented Generation (RAG) to fetch relevant information directly from uploaded insurance documents and generate reliable, context-aware responses.


🔹 What makes InsureMind special?


Unlike traditional chatbots, InsureMind not only provides answers but also ensures full transparency and explainability by showing exactly which PDF document, page number, reference source, and supporting excerpt the answer was derived from making the responses trustworthy and verifiable.

This helps users confidently verify policy information directly from the source documents instead of blindly trusting generated responses.


🔹 Dataset Used:


For building this project, I collected 9 real insurance policy PDF documents across multiple domains:

📌 Cyber Security Insurance – ICICI Lombard, TATA AIG, HDFC ERGO

📌 Health Insurance – HDFC ERGO

📌 Vehicle Insurance – TATA AIG, HDFC ERGO


🔹 What this project does:


✅ Answers insurance policy questions intelligently

✅ Understands multiple PDF insurance documents (Vehicle, Cyber Security, Healthcare, etc.)

✅ Provides document-grounded responses with exact source references

✅ Displays the PDF name, page number, and supporting excerpt used to generate answers

✅ Enables transparent and explainable AI-based document intelligence

✅ Reduces hallucinations using grounded retrieval-based response generation

✅ Works fully offline with local LLM integration


🛠 What I built in this project:



🔹 Developed a complete RAG pipeline for document question answering

🔹 Processed and indexed insurance PDFs for intelligent semantic retrieval

🔹 Implemented document chunking + embedding generation for contextual search

🔹 Used BAAI/bge-base-en-v1.5 for semantic embedding generation

🔹 Chose ChromaDB specifically for efficient metadata handling (PDF source name, page number, evidence snippets) to enable accurate source traceability

🔹 Added cross-encoder/ms-marco-MiniLM-L-6-v2 reranking to improve evidence relevance and retrieval precision

🔹 Integrated Llama 3.2 3B via Ollama for grounded local response generation

🔹 Applied prompt engineering strategies to improve answer reliability and reduce hallucinations

🔹 Built a complete interactive Streamlit web application UI

🔹 Designed chatbot conversation flow with source tracking, PDF references, citations, and excerpt display

🔹 Enabled fully local AI execution without paid API dependency

💻 Tech Stack:

Python | Streamlit | LangChain | ChromaDB | Ollama | Llama 3.2 3B | HuggingFace | BGE Embeddings | CrossEncoder | NLP | RAG
