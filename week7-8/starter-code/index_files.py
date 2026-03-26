"""Index text files from a folder into ChromaDB and query them."""

import os
import sys
import chromadb

if len(sys.argv) < 2:
    print("Usage: python index_files.py <folder_path>")
    print("Example: python index_files.py ~/my_notes")
    sys.exit(1)

folder = os.path.expanduser(sys.argv[1])

if not os.path.isdir(folder):
    print(f"Error: {folder} is not a directory")
    sys.exit(1)

# --- Read all .txt files ---
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

    # Split into chunks of ~500 characters at paragraph breaks
    chunks = text.split("\n\n")
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if len(chunk) < 20:
            continue
        doc_id = f"{filename}_{i}"
        documents.append(chunk)
        doc_ids.append(doc_id)

print(f"Found {len(documents)} chunks from {folder}\n")

if not documents:
    print("No .txt files with content found.")
    sys.exit(1)

# --- Index into ChromaDB ---
client = chromadb.Client()
collection = client.create_collection("my_files")
collection.add(documents=documents, ids=doc_ids)

print(f"Indexed {len(documents)} chunks. Ready to query.\n")
print("Type a question to search your documents. Type 'quit' to exit.\n")

while True:
    query = input("Search: ")
    if query.lower() == "quit":
        break

    results = collection.query(query_texts=[query], n_results=3)

    print()
    for i, doc in enumerate(results["documents"][0]):
        source = results["ids"][0][i]
        print(f"  [{source}]")
        print(f"  {doc[:200]}{'...' if len(doc) > 200 else ''}")
        print()
