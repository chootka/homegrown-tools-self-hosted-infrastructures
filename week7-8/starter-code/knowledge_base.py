"""Personal knowledge base — indexes your documents and answers questions using RAG."""

import os
import sys
import chromadb
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "tinyllama"  # Change to "llama3.2:3b" if you have 8GB RAM

if len(sys.argv) < 2:
    print("Usage: python knowledge_base.py <folder_path>")
    print("Example: python knowledge_base.py ~/my_notes")
    sys.exit(1)

folder = os.path.expanduser(sys.argv[1])

if not os.path.isdir(folder):
    print(f"Error: {folder} is not a directory")
    sys.exit(1)

# --- Step 1: Read and chunk documents ---
documents = []
doc_ids = []

for filename in sorted(os.listdir(folder)):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(folder, filename)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().strip()

    if not text:
        continue

    chunks = text.split("\n\n")
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if len(chunk) < 20:
            continue
        documents.append(chunk)
        doc_ids.append(f"{filename}_{i}")

if not documents:
    print("No .txt files with content found.")
    sys.exit(1)

# --- Step 2: Index into ChromaDB ---
print(f"Indexing {len(documents)} chunks from {folder}...")
client = chromadb.Client()
collection = client.create_collection("knowledge_base")
collection.add(documents=documents, ids=doc_ids)
print(f"Done. Ready to answer questions.\n")
print("Ask questions about your documents. Type 'quit' to exit.\n")

# --- Step 3: Query loop ---
while True:
    question = input("You: ")
    if question.lower() == "quit":
        break

    # Retrieve relevant chunks
    results = collection.query(query_texts=[question], n_results=3)
    chunks = results["documents"][0]

    # Show what was retrieved
    print(f"\n  [Found {len(chunks)} relevant chunks]")
    for i, chunk in enumerate(chunks):
        source = results["ids"][0][i]
        preview = chunk[:80].replace("\n", " ")
        print(f"    {source}: {preview}...")
    print()

    # Build the prompt
    context = "\n---\n".join(chunks)
    prompt = f"""You are a helpful assistant. Answer the question based on the provided context.
If the context doesn't contain enough information, say so. Be concise.

Context:
{context}

Question: {question}

Answer:"""

    # Generate answer
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        })
        answer = response.json()["response"]
        print(f"Answer: {answer}\n")
    except requests.ConnectionError:
        print("Error: Can't connect to Ollama. Is it running? (ollama serve)\n")
