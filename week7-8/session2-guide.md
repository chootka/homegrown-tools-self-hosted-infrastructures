# Session 2: RAG — Ask Questions About Your Own Documents

## What We're Doing

Last session we got a local LLM running on the Pi. But it only knows what it was trained on — it can't answer questions about your notes, your PDFs, your research.

Today we fix that. We'll build a RAG (Retrieval-Augmented Generation) pipeline:
1. **Index** your documents into a vector database
2. **Retrieve** the relevant chunks when you ask a question
3. **Generate** an answer using your local LLM + those chunks

Everything runs locally. Your documents never leave your Pi.

---

## What is RAG?

**The problem:** An LLM on its own only knows what was in its training data. Ask it about your lecture notes and it either makes something up or says "I don't know."

**The solution:** Before asking the LLM, search your documents for relevant chunks and include them in the prompt.

```
Without RAG:
  You: "When is the week 5 assignment due?"
  LLM: "I don't have that information."

With RAG:
  You: "When is the week 5 assignment due?"
  System finds the relevant chunk from your syllabus
  LLM sees the chunk + your question
  LLM: "The deadline is Friday October 18th."
```

Three steps:
1. **Index** — Split documents into chunks, convert to vectors, store in a database
2. **Retrieve** — Convert the question to a vector, find the most similar chunks
3. **Generate** — Feed those chunks + the question to the LLM

---

## Part 1: Embeddings + Vector Database (60 min)

### 1. Install ChromaDB on the Pi

```bash
cd ~/local-llm
source venv/bin/activate
pip install chromadb
```

### 2. What are embeddings?

A sentence gets converted into a list of numbers (a vector). Similar sentences produce similar numbers. A vector database stores these and lets you search by similarity.

```
"TCP uses a three-way handshake"  → [0.12, -0.34, 0.56, ...]
"UDP is connectionless"          → [0.11, -0.31, 0.48, ...]  ← similar topic, similar numbers
"My cat likes tuna"              → [-0.72, 0.15, -0.03, ...] ← different topic, different numbers
```

### 3. Run the index example

```bash
python index_docs.py
```

(File is in `starter-code/index_docs.py`)

This stores 5 documents in Chroma and queries for similar ones. Look at the output — it returns the most relevant documents, not an exact keyword match.

### 4. Try different queries

Edit the query in the script. Try:
- "how do devices communicate wirelessly?"
- "what protocol translates names to addresses?"
- "low power long range communication"

Notice how it finds relevant documents even when you don't use the exact same words.

---

## Part 2: Full RAG Pipeline (60 min)

### 5. Run the RAG script

```bash
python rag.py
```

(File is in `starter-code/rag.py`)

This combines retrieval + generation:
1. You ask a question
2. Chroma finds the 2 most relevant chunks
3. Those chunks get injected into the prompt
4. Ollama generates an answer based on those chunks

### 6. Test with and without context

Try asking: "When is the week 5 assignment due?"
- With RAG → it finds the syllabus chunk and gives the correct date
- Without RAG (just ask Ollama directly) → it doesn't know

This is the whole point. The LLM is grounded in your data.

### 7. Index your own documents

Now use your own notes. The script `index_files.py` reads text files from a folder:

```bash
# Put some .txt files in a folder
mkdir ~/my_notes
# Copy or create some text files there

python index_files.py ~/my_notes
```

(File is in `starter-code/index_files.py`)

Then ask questions about your own documents.

---

## Part 3: Make It Yours (60 min)

### 8. Build your personal knowledge base

Combine everything into a single app that:
- Indexes your documents on startup
- Lets you ask questions in a loop
- Retrieves relevant context and generates answers

```bash
python knowledge_base.py ~/my_notes
```

(File is in `starter-code/knowledge_base.py`)

### 9. Experiment

Try:
- Indexing different kinds of documents
- Changing the number of chunks retrieved (`n_results`)
- Changing the model (if you have 8GB: `llama3.2:3b` is smarter than `tinyllama`)
- Changing the prompt template

### 10. Discussion

What we built:
- A fully local, private knowledge base
- Your documents → your embeddings → your vector DB → your LLM → your answer
- Nothing leaves the machine
- Cost: $0 forever
- No API keys, no rate limits, no terms of service

---

## The Full Stack

```
Your documents
    ↓
Split into chunks
    ↓
Embedding model (Chroma's built-in) converts to vectors
    ↓
ChromaDB stores the vectors
    ↓
You ask a question
    ↓
Question → vector → find similar chunks
    ↓
Relevant chunks + question → Ollama (local LLM)
    ↓
Answer grounded in your data
```

Every piece of this runs on the Raspberry Pi sitting in front of you.
