# Session 3: RAG Pipeline — Ask Questions About Your Own Documents

## Context

Students have been building a self-hosted AI ecosystem on Raspberry Pis. They're running local LLMs (Ollama) that respond to Meshtastic radio messages and can control a live website via MQTT.

## What's Already Set Up

Each student has (or should have):
- A Raspberry Pi 5 with Ollama installed (`tinyllama` model)
- The `channels` app cloned at `~/channels` with a `.env` configured
- A Meshtastic device plugged into their Pi via USB
- A second Meshtastic device paired to their phone via Bluetooth
- Channels 3-7 configured on their Meshtastic devices

The shared infrastructure:
- MQTT broker at `dweb2025.nohost.me:1883`
- Live website at `https://mqtt.dweb2025.nohost.me`
- Website reacts to commands: `blue`, `red`, `purple`, `stripes`, `hide`, `show`, `rotate`, `reset`

## How to Start Everything

Each student SSHs into their Pi:
```bash
ssh username@their-pi-address
cd ~/channels
source venv/bin/activate
python main.py
```

Should see:
```
[router] Loaded X channels: ...
[main] Connecting to Meshtastic device...
[main] Using LOCAL Ollama.
[main] Listening for messages. Ctrl+C to quit.
```

If Ollama isn't running: `ollama serve &`

## The Channels

Each student's `.env` has `ACTIVE_CHANNELS=X` so they only respond on their assigned channel:

| Channel | Name | Agent | What it does |
|---|---|---|---|
| 3 | sysop | admin | BBS-style operator, handles `!` commands |
| 4 | sheila | conversational | Sarcastic but helpful assistant |
| 5 | webmistress | webmistress | Controls the website — try `blue`, `rotate`, `storytime` |
| 6 | lowviz | ascii_visual | Responds only in ASCII art patterns |
| 7 | mmmmmmorse | conversational | Translates everything to/from Morse code |

Students send messages from their phone's Meshtastic app on the appropriate channel.

## Quick Recap: Things to Demo/Try

### Website control (channel 5)
Send these on channel 5:
- `blue`, `red`, `purple` — change background
- `rotate` — spin the page
- `stripes` — diagonal pattern
- `hide` — redact all text
- `reset` — undo everything
- `storytime` — agent starts telling a noir story, posts to website AND radio
- `stop` — ends storytime

### Agent customization
Students can edit `~/channels/channels_ollama.yaml` to change system prompts. For example, change sheila's personality:
```yaml
  4:
    agent: conversational
    name: "sheila"
    system_prompt: "You are a pirate. Respond to everything like a pirate captain. Under 200 characters."
```
Then restart the app.

### Test with each other
Students can message each other's agents across the mesh. One person sends a message on channel 4, the student running channel 4 sees it in their terminal and their agent responds.

---

## This Session: RAG Pipeline

The detailed step-by-step is in `session2-guide.md` (`week7-9/session2-guide.md`). Here's the overview:

### What is RAG?

RAG (Retrieval-Augmented Generation) makes an LLM answer questions about YOUR data — documents it was never trained on. Three steps:

1. **Index** — split your documents into chunks, convert to vectors, store in a database
2. **Retrieve** — when you ask a question, find the most relevant chunks
3. **Generate** — feed those chunks + your question to the LLM

Without RAG, the LLM guesses. With RAG, it answers from your documents.

### Part 1: Embeddings + Vector Database (60 min)

1. Explain what RAG is (use the glossary at `week7-9/glossary.md` — has diagrams)
2. Students install ChromaDB on their Pis:
   ```bash
   cd ~/channels
   source venv/bin/activate
   pip install chromadb
   ```
3. Run `index_docs.py` — stores sample documents, queries by similarity
4. Students try different queries to see how vector search works (it matches by meaning, not keywords)

### Part 2: Full RAG Pipeline (60 min)

1. Run `rag.py` — combines retrieval + Ollama generation
2. Key demo: ask "When is the week 5 assignment due?" — with RAG it answers correctly, without RAG it doesn't know
3. Run `index_files.py ~/my_notes` — students index their own text files

### Part 3: Build Your Own Knowledge Base (60 min)

1. Run `knowledge_base.py ~/my_notes` — the full pipeline in one script
2. Students experiment: different documents, different queries, tweak the prompt
3. Discussion: everything runs locally, no cloud, no cost, your data stays on your device

### Starter code locations

All scripts are in `week7-9/starter-code/` in the course repo, each in its own folder with a `requirements.txt`. Students can either type the code from the guide or clone the repo and run them directly:

```bash
cd ~/homegrown-tools-self-hosted-infrastructures/week7-9/starter-code/rag
pip install -r requirements.txt
python rag.py
```

### Important note

The RAG scripts use Ollama at `localhost:11434` — make sure Ollama is running on each Pi before starting. If not: `ollama serve &`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Permission denied` on serial port | `sudo usermod -a -G dialout $USER` then log out/in |
| Ollama not running | `ollama serve &` |
| No serial device found | Check cable, try different USB port, `ls /dev/ttyUSB* /dev/ttyACM*` |
| Agent gives weird long responses | Tinyllama is small — make system prompts shorter and more explicit |
| Website not changing | Check `dweb2025.nohost.me:1883` is reachable: `mosquitto_pub -h dweb2025.nohost.me -p 1883 -t 'test' -m 'hello'` |
| Multiple agents responding to same message | Check `.env` — each student needs a different `ACTIVE_CHANNELS` value |
| Heltec v4 not detected | Uses `/dev/ttyACM0` not `ttyUSB0`. May need firmware reflash |
| `meshtastic` command not found | `cd ~/channels && source venv/bin/activate` |

## Key Files

| File | What it does |
|---|---|
| `channels_ollama.yaml` | Agent definitions — edit system prompts here |
| `.env` | Configuration — broker, active channels, LLM mode |
| `agents/base_ollama.py` | The Ollama API call (the core) |
| `agents/webmistress.py` | Website control + storytime agent |
| `main.py` | Entry point — runs the whole app |
| `router.py` | Routes messages to the right agent by channel index |

## Links

- Course repo: https://github.com/chootka/homegrown-tools-self-hosted-infrastructures
- Channels repo: https://github.com/chootka/channels
- Website: https://mqtt.dweb2025.nohost.me
- Glossary: `week7-9/glossary.md` in the course repo
- Walkthrough guide: `week7-9/walkthrough-guide.md`
- Session 2 (RAG details): `week7-9/session2-guide.md`
