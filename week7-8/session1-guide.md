# Session 1: Cloud API → Local LLM

## What We're Doing

We're going to talk to an AI two ways:
1. First via the cloud (Claude API) — your data leaves your machine
2. Then locally on a Raspberry Pi (Ollama) — nothing leaves the device

By the end, you'll understand what an API call looks like, why local matters, and have a working local LLM on your Pi.

---

## Part 1: Setup (30 min)

### 1. Get your Pi running

- Power on your Raspberry Pi
- Connect to the network
- SSH in from your laptop:

```bash
ssh your-username@your-pi-address
```

### 2. Demo: Channels (instructor only)

Your instructor will demo a real project that runs Claude AI agents on Meshtastic radio channels. You can browse the code at https://github.com/chootka/channels — we'll walk through how it works together.

The key takeaway: the entire Claude API interaction is about 10 lines of Python.

### 3. Set up Python on your laptop

```bash
mkdir ~/claude-lab
cd ~/claude-lab
python3 -m venv venv
source venv/bin/activate
pip install anthropic
```

### 4. Set the API key

Your instructor will give you a shared API key. Set it in your terminal:

```bash
export ANTHROPIC_API_KEY="paste-the-key-here"
```

This only lives in this terminal session — it's not saved anywhere.

---

## Part 2: Understanding the Claude API (45 min)

### 5. Walk through the channels code

Let's look at how a real project talks to Claude. Browse the code at https://github.com/chootka/channels and open these files:

**`channels.yaml`** — defines AI agents, one per radio channel:
```yaml
channels:
  4:
    agent: conversational
    name: "sheila"
    system_prompt: "You are Sheila, a dry-witted assistant..."
```

**`agents/base.py`** — the actual API call (this is the important part):
```python
# Create a client
self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

# Send a message and get a response
response = self.client.messages.create(
    model=self.model,
    max_tokens=self.max_tokens,
    system=system_prompt,       # tells the AI how to behave
    messages=[{"role": "user", "content": message}],  # the user's question
)

# Get the text out
text = response.content[0].text
```

That's it. That's the entire interaction with Claude. Everything else in the project is plumbing — routing radio messages, rate limiting, logging.

**`main.py`** — the message flow:
1. A radio message arrives
2. The router picks the right agent based on channel number
3. The agent sends the message to Claude
4. Claude's response goes back out over radio

### 6. Write your first API script

Inside your `claude-lab` folder, create a file called `hello_claude.py`:

```python
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=256,
    system="You are a helpful assistant. Be concise.",
    messages=[{"role": "user", "content": "What is a mesh network?"}],
)

print(response.content[0].text)
```

Run it:

```bash
python hello_claude.py
```

Try changing the question. Try changing the system prompt. What happens if you tell it to respond in a different language? In haiku?

(A copy of this file is also in the course repo at `starter-code/hello_claude.py`)

### 7. Make it interactive

Create `chat_claude.py` in your `claude-lab` folder:

```python
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

print("Chat with Claude. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=256,
        system="You are a helpful assistant. Be concise.",
        messages=[{"role": "user", "content": user_input}],
    )

    print(f"Claude: {response.content[0].text}\n")
```

Run it:

```bash
python chat_claude.py
```

Type questions, have a conversation. Type `quit` to exit.

(A copy of this file is also in the course repo at `starter-code/chat_claude.py`)

### 8. Discussion: what just happened?

Think about this:
- Your question left your laptop, traveled to Anthropic's servers, and came back
- You need an API key — someone controls your access
- You need internet — no connection, no AI
- It costs money — every message is metered
- Anthropic can see every question you ask

**What if we could do all of this locally, on a device we own?**

---

## Part 3: Install Ollama on the Pi (45 min)

### 9. SSH into your Pi

```bash
ssh your-username@your-pi-address
```

### 10. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This installs Ollama, which runs LLMs locally.

### 11. Pull a model

For 4GB Pi:
```bash
ollama pull tinyllama
```

For 8GB Pi:
```bash
ollama pull llama3.2:3b
```

This downloads the model to your Pi. It's a one-time download — after this, no internet needed.

### 12. Test it

```bash
ollama run tinyllama "What is a mesh network?"
```

It will take a moment — the Pi is doing all the computation locally.

---

## Part 4: Talk to Ollama from Python (45 min)

### 14. Set up Python on the Pi

```bash
mkdir ~/local-llm
cd ~/local-llm
python3 -m venv venv
source venv/bin/activate
pip install requests
```

### 15. Run the hello script

Copy `hello_ollama.py` to your Pi and run it:

```bash
python hello_ollama.py
```

(File is in `starter-code/hello_ollama.py`)

Ollama has a simple HTTP API at `http://localhost:11434`. You send a JSON request, you get a JSON response. No API key needed.

### 16. Make it interactive

```bash
python chat_ollama.py
```

(File is in `starter-code/chat_ollama.py`)

Same chat loop as the Claude version, but everything runs on the Pi.

### 17. Compare cloud vs local

| | Claude (cloud) | Ollama (local) |
|---|---|---|
| Speed | Fast | Slower, but no network latency |
| Quality | Very smart | Simpler, but capable |
| Privacy | Data goes to Anthropic | Nothing leaves the Pi |
| Cost | Pay per token | Free forever |
| Internet | Required | Not needed |
| Control | Anthropic's rules | Your rules |

---

## Homework Before Session 2

Gather some personal documents you'd like to make searchable:
- Course notes
- PDFs
- Text files
- Bookmarks or articles

Next session, we'll build a system that indexes your documents and lets you ask questions about them — all running locally on your Pi.
