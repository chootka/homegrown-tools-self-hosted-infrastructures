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

A database optimized for storing and searching vectors. You put your documents in (as vectors), and then search by similarity — "find me documents similar to this question." ChromaDB is a simple one that runs locally.

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
