import chromadb
import requests

# --- Set up vector database with some sample docs ---
db = chromadb.Client()
collection = db.create_collection("notes")

collection.add(
    documents=[
        "The assignment for week 5 is due Friday October 18th",
        "TCP uses congestion control to avoid overwhelming the network",
        "Meshtastic devices communicate over LoRa at 868 MHz in Europe",
        "Ollama runs LLMs locally on your machine with no internet required",
        "A vector database stores embeddings and allows similarity search",
        "RAG stands for Retrieval-Augmented Generation",
    ],
    ids=["1", "2", "3", "4", "5", "6"],
)

print("RAG demo — ask questions about the indexed documents.")
print("Type 'quit' to exit.\n")

while True:
    question = input("You: ")
    if question.lower() == "quit":
        break

    # Step 1: Retrieve relevant chunks
    results = collection.query(query_texts=[question], n_results=2)
    chunks = results["documents"][0]

    print(f"\n  [Retrieved chunks:]")
    for chunk in chunks:
        print(f"    → {chunk}")
    print()

    # Step 2: Build prompt with context
    context = "\n".join(chunks)
    prompt = f"""Based on the following context, answer the question. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer concisely:"""

    # Step 3: Generate answer with local LLM
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
    })

    print(f"LLM: {response.json()['response']}\n")
