# AI Glossary for Self-Hosters

A plain-language glossary of AI terms, focused on what matters when you're running things yourself.

---

## The Stack

Here's how all the pieces fit together, from bottom to top:

```
┌─────────────────────────────────────────────────────────────┐
│                        YOU (the user)                       │
│                  "What did we cover in week 3?"             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                      │
│                                                             │
│  Your script, web app, chatbot, CLI tool, etc.              │
│  This is the code YOU write.                                │
│                                                             │
│  Examples: chat_ollama.py, knowledge_base.py, channels app  │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌───────────────────────┐ ┌───────────────────────────────────┐
│    RETRIEVAL (RAG)    │ │                                   │
│                       │ │                                   │
│  Vector Database      │ │        INFERENCE ENGINE           │
│  (ChromaDB)           │ │                                   │
│                       │ │  Runs the model, does the         │
│  Stores your docs as  │ │  actual text generation.          │
│  vectors. Finds       │ │                                   │
│  relevant chunks      │ │  Cloud: Anthropic API, OpenAI API │
│  when you ask a       │ │  Local: Ollama, llama.cpp         │
│  question.            │ │                                   │
│                       │ │                                   │
│  Uses an EMBEDDING    │ │  Uses an LLM (Large Language      │
│  MODEL to convert     │ │  Model) to generate responses.    │
│  text → vectors.      │ │                                   │
└───────────┬───────────┘ └──────────────┬────────────────────┘
            │                            │
            └────────────┬───────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         THE MODEL                           │
│                                                             │
│  A giant file of numbers (weights) that represents          │
│  patterns learned from text.                                │
│                                                             │
│  Cloud models:  Claude, GPT-4, Gemini                       │
│  Local models:  TinyLlama (1.1B), Phi-3 (3.8B),            │
│                 Llama 3.2 (3B), Mistral (7B)                │
│                                                             │
│  Bigger = smarter but slower and needs more RAM.            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                        HARDWARE                             │
│                                                             │
│  Cloud: Nvidia A100/H100 GPUs in a data center              │
│  Local: Your Raspberry Pi 5 (ARM CPU, 4-8GB RAM)           │
│                                                             │
│  The model runs on whatever hardware you have.              │
│  Smaller models = can run on small devices.                 │
└─────────────────────────────────────────────────────────────┘
```

---

## The RAG Pipeline (Zoomed In)

```
YOUR DOCUMENTS                          YOUR QUESTION
(notes, PDFs, text files)               "What is TCP congestion control?"
        │                                        │
        ▼                                        ▼
┌──────────────┐                       ┌──────────────────┐
│  Split into  │                       │  Convert to a    │
│  chunks      │                       │  vector          │
│  (paragraphs)│                       │  (embedding)     │
└──────┬───────┘                       └────────┬─────────┘
       │                                        │
       ▼                                        ▼
┌──────────────┐                       ┌──────────────────┐
│  Convert     │                       │  Search for      │
│  each chunk  │                       │  similar vectors │
│  to a vector │                       │  in the database │
│  (embedding) │                       │                  │
└──────┬───────┘                       └────────┬─────────┘
       │                                        │
       ▼                                        ▼
┌──────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE                        │
│                      (ChromaDB)                          │
│                                                          │
│  chunk_1: "TCP uses a three-way handshake..."  [0.12..]  │
│  chunk_2: "UDP is connectionless..."           [0.11..]  │
│  chunk_3: "TCP congestion control avoids..."   [0.14..]  │ ← match!
│  chunk_4: "DNS translates domain names..."     [-0.3..]  │
└──────────────────────────┬───────────────────────────────┘
                           │
                    top 2-3 matches
                           │
                           ▼
              ┌─────────────────────────┐
              │  Build a PROMPT:        │
              │                         │
              │  "Context:              │
              │   TCP congestion        │
              │   control avoids...     │
              │                         │
              │   Question:             │
              │   What is TCP           │
              │   congestion control?   │
              │                         │
              │   Answer:"              │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  LOCAL LLM (Ollama)     │
              │                         │
              │  Generates an answer    │
              │  based on the context   │
              │  you provided.          │
              └────────────┬────────────┘
                           │
                           ▼
              "TCP congestion control is a
               mechanism that prevents a sender
               from overwhelming the network..."
```

---

## Glossary

### LLM (Large Language Model)

A program that predicts the next word in a sequence. It was trained on massive amounts of text and learned patterns of language. When you "chat" with an AI, you're sending text to an LLM and it's predicting what text should come next.

Examples: Claude, GPT-4, Llama, TinyLlama, Mistral, Phi-3

### Model

A file containing billions of numbers (called "weights" or "parameters") that encode language patterns. When people say "download a model," they mean download this file. Model sizes are measured in parameters:

- **1B (1 billion)** — small, runs on a Pi, basic quality (TinyLlama)
- **3B** — better quality, still runs on a Pi with 8GB (Llama 3.2, Phi-3 mini)
- **7B** — good quality, needs a decent computer (Mistral, Llama 2)
- **70B+** — excellent quality, needs serious hardware or a cloud GPU
- **Claude, GPT-4** — unknown size, only available via cloud API

### Parameters / Weights

The numbers inside a model. During training, these numbers are adjusted so the model gets better at predicting text. More parameters = more capacity to learn = smarter but bigger and slower.

### Inference

The act of running a model to generate output. When you type a question and the model responds, that's inference. This is what Ollama does on your Pi.

### Token

The unit of text that an LLM processes. Roughly 1 token ≈ ¾ of a word, or about 4 characters. "Hello world" is 2 tokens. "Raspberry Pi" is 2-3 tokens. API pricing is per-token.

### Prompt

The text you send to the model. Has two parts:
- **System prompt** — instructions for how the model should behave ("You are a helpful assistant")
- **User prompt** — the actual question or input from the user

### Context Window

How much text the model can "see" at once — both your input and its output. Measured in tokens. If the context window is 4096 tokens, that's roughly 3000 words total. Longer context windows are more expensive and slower.

### System Prompt

Hidden instructions that shape the model's behavior. The user doesn't see them, but they control personality, rules, and style. Example: "You are Sheila, a dry-witted assistant. Keep responses under 200 characters."

### API (Application Programming Interface)

A way to talk to a service over the internet. The Claude API lets your Python script send a question to Anthropic's servers and get a response back. You need an API key and internet access.

### API Key

A secret string that identifies you to an API. Like a password for your account. It's how the service knows who to bill and whether you're authorized. Never put it in code — use environment variables.

### Ollama

A tool that runs LLMs locally on your machine. It downloads models, manages them, and provides a simple HTTP API at `localhost:11434`. No API key, no internet, no cost.

### Embedding

Converting text into a list of numbers (a vector) that captures its meaning. Similar texts produce similar vectors. This is how you make text searchable by meaning instead of keywords.

```
"cats like fish"     → [0.2, -0.1, 0.8, ...]
"dogs enjoy meat"    → [0.3, -0.1, 0.7, ...]  ← similar meaning, similar numbers
"quantum physics"    → [-0.5, 0.9, -0.2, ...]  ← different meaning, different numbers
```

### Embedding Model

A model specifically designed to convert text into vectors. Different from a language model — it doesn't generate text, it just maps text to numbers. ChromaDB includes a built-in embedding model. Ollama can also run embedding models.

### Vector

A list of numbers. In AI, vectors represent the "meaning" of a piece of text in mathematical space. Similar meanings = nearby vectors. A typical embedding vector has 384-1536 numbers in it.

### Vector Database

A database designed for searching by meaning instead of by exact match.

**How a traditional (relational) database works:**

You store structured rows and columns. You search with exact queries.

```
┌────────┬──────────────────────────────────┬──────────┐
│  id    │  title                           │  year    │
├────────┼──────────────────────────────────┼──────────┤
│  1     │  Introduction to Networking      │  2024    │
│  2     │  TCP/IP Fundamentals             │  2023    │
│  3     │  Wireless Mesh Protocols         │  2024    │
└────────┴──────────────────────────────────┴──────────┘

Query: SELECT * FROM docs WHERE title LIKE '%networking%'
Result: Row 1 (exact keyword match)
```

This only works if you know the exact word. Searching for "how computers talk to each other" returns nothing — even though row 1 and 2 are both relevant.

**How a vector database works:**

Instead of rows and columns, you store text as vectors (lists of numbers that represent meaning). You search by asking "what's closest to this meaning?"

```
Store:
  "Introduction to Networking"     → [0.82, -0.15, 0.44, 0.31, ...]
  "TCP/IP Fundamentals"            → [0.79, -0.12, 0.41, 0.28, ...]
  "Wireless Mesh Protocols"        → [0.71, -0.08, 0.52, 0.19, ...]
  "French Pastry Techniques"       → [-0.33, 0.67, -0.21, 0.55, ...]

Query: "how computers talk to each other"
       → [0.80, -0.14, 0.43, 0.30, ...]

Find nearest vectors:
  1. "Introduction to Networking"   (distance: 0.03)  ← very close!
  2. "TCP/IP Fundamentals"          (distance: 0.06)  ← close!
  3. "Wireless Mesh Protocols"      (distance: 0.15)  ← somewhat close
  4. "French Pastry Techniques"     (distance: 1.87)  ← far away
```

The query "how computers talk to each other" doesn't share any keywords with "TCP/IP Fundamentals" — but the vector database knows they're about the same topic because their vectors are close together in mathematical space.

**Think of it like a library:**

- A relational database is like searching a card catalog by exact title. You need to know the words.
- A vector database is like asking a librarian "I'm looking for something about how computers communicate." The librarian understands the meaning of your request and walks you to the right shelf — even if none of the book titles contain the word "communicate."

**The key difference:**

| | Relational DB | Vector DB |
|---|---|---|
| Stores | Structured rows/columns | Vectors (lists of numbers) |
| Searches by | Exact match, keywords | Similarity of meaning |
| Query | `WHERE title LIKE '%network%'` | "find things close to this vector" |
| Understands synonyms? | No | Yes |
| Needs exact words? | Yes | No |
| Used for | Traditional apps, user data | AI, search, recommendations |

**How it works under the hood:**

1. You give it a piece of text: "TCP uses a three-way handshake"
2. An embedding model converts it to a vector: `[0.12, -0.34, 0.56, ...]` (hundreds of numbers)
3. The database stores this vector alongside the original text
4. When you query, your question also becomes a vector
5. The database finds stored vectors that are closest (using math like cosine similarity)
6. It returns the original text associated with those vectors

ChromaDB handles steps 2 and 5 automatically — you just give it text and ask questions. That's why our example code is so simple:

```python
# Store
collection.add(documents=["TCP uses a three-way handshake"], ids=["1"])

# Search by meaning
results = collection.query(query_texts=["how do connections get established?"])
# Returns: "TCP uses a three-way handshake"
```

No keyword matching. No SQL. Just meaning.

### RAG (Retrieval-Augmented Generation)

A pattern for making LLMs answer questions about your data. Three steps:
1. **Retrieve** — find relevant chunks from your documents using a vector database
2. **Augment** — add those chunks to the prompt as context
3. **Generate** — the LLM generates an answer using that context

Without RAG, the LLM can only use what it was trained on. With RAG, it can use your documents.

### Chunk

A piece of a document. Since models have limited context windows, you can't feed them entire books. Instead, you split documents into smaller pieces (chunks) — usually paragraphs or sections — and store each one separately. During retrieval, you find the most relevant chunks.

### Hallucination

When an LLM makes something up that sounds confident but is wrong. Without RAG, if you ask about your course syllabus, it might invent a plausible-sounding but totally fake answer. RAG reduces hallucination by grounding the model in your actual documents.

### Fine-tuning

Retraining a model on your specific data to change its behavior permanently. Different from RAG — fine-tuning modifies the model itself, while RAG just gives it extra context at query time. Fine-tuning is expensive and complex. RAG is cheap and easy. For most use cases, RAG is what you want.

### Quantization

Compressing a model by reducing the precision of its numbers (e.g., from 32-bit to 4-bit). Makes the model smaller and faster at the cost of some quality. This is why models can run on a Raspberry Pi — they're quantized down to fit in limited RAM. Ollama handles this automatically.

### Temperature

A setting that controls how "creative" or "random" the model's output is. Temperature 0 = very predictable, always picks the most likely next word. Temperature 1 = more varied, sometimes surprising. Higher values = more creative but also more likely to hallucinate.

### Latency

How long it takes to get a response. Cloud APIs have network latency (your data travels to the server and back) plus compute time. Local models have no network latency but may be slower at compute (especially on a Pi).

### Open-Source / Open-Weight Models

Models whose weights are publicly available for download. You can run them yourself, modify them, and use them without permission. Examples: Llama, Mistral, Phi, TinyLlama. This is what makes self-hosting possible. Contrast with "closed" models like Claude and GPT-4, which are only accessible via API.

---

## Cloud vs Local — At a Glance

```
┌──────────────────────┬───────────────────────────────────┐
│       CLOUD          │            LOCAL                  │
│                      │                                   │
│  ┌────────────┐      │      ┌────────────┐              │
│  │  Your      │      │      │  Your      │              │
│  │  Laptop    │      │      │  Laptop    │              │
│  └─────┬──────┘      │      └─────┬──────┘              │
│        │ internet    │            │ USB / local network  │
│        ▼             │            ▼                      │
│  ┌────────────┐      │      ┌────────────┐              │
│  │  Anthropic │      │      │  Your Pi   │              │
│  │  / OpenAI  │      │      │  (Ollama)  │              │
│  │  servers   │      │      │            │              │
│  └────────────┘      │      └────────────┘              │
│                      │                                   │
│  ✗ Data leaves       │  ✓ Data stays on your device     │
│  ✗ Needs internet    │  ✓ Works offline                 │
│  ✗ Costs money       │  ✓ Free forever                  │
│  ✗ They control it   │  ✓ You control it                │
│  ✓ Very smart        │  ✗ Less smart (smaller models)   │
│  ✓ Very fast         │  ✗ Slower on small hardware      │
└──────────────────────┴───────────────────────────────────┘
```
