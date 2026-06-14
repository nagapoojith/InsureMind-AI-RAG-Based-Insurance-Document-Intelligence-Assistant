from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

DB_PATH = "./chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embedding_model
)

# CHANGE QUERY HERE FOR TESTING
query = "What is covered in health insurance?"

results = vector_db.similarity_search(query, k=3)

print("\nQuery:", query)
print("\nTop Matching Results:\n")

for i, doc in enumerate(results):
    print(f"Result {i+1}")
    print("Source PDF:", doc.metadata.get("source"))
    print("Page Number:", doc.metadata.get("page"))
    print("\nContent:")
    print(doc.page_content[:1000])
    print("\n" + "=" * 100 + "\n")