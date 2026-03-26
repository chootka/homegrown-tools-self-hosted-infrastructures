# How the Channels Code Works

The `channels` repo (https://github.com/chootka/channels) runs Claude AI agents on Meshtastic radio channels. Here's a walkthrough of every file.

## The Big Picture

```
Someone sends a radio message
    → Pi receives it over USB serial
    → Python routes it to the right AI agent
    → Agent sends it to Claude's API
    → Claude responds
    → Pi sends the response back over radio
```

## The Files

### `main.py` — The Starting Point

Does three things:
1. Connects to the Meshtastic radio over USB serial
2. Subscribes to incoming messages
3. Sits in a loop waiting

When a message arrives, `on_receive()` hands it to the router. Whatever comes back gets sent out over radio:

```python
response = agent.handle(text, sender, mesh_context=mesh_ctx)
iface.sendText(response, channelIndex=channel)
```

### `config.py` — All Settings in One Place

Everything comes from environment variables:

```python
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SERIAL_PORT = os.environ.get("MESHTASTIC_SERIAL_PORT", None)
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
MAX_MESSAGE_BYTES = 220  # LoRa message size limit
```

### `channels.yaml` — Agent Definitions

Each radio channel gets a different AI personality:

```yaml
channels:
  3:
    agent: admin
    name: "sysop"         # talks like a '90s BBS operator
  4:
    agent: conversational
    name: "sheila"         # dry-witted, sarcastic helper
  5:
    agent: residue
    name: "rezzy"          # weaves memory with simulated corruption
  6:
    agent: ascii_visual
    name: "lowviz"         # responds only in ASCII art
  7:
    agent: conversational
    name: "mmmmmmorse"     # responds in Morse code
```

### `router.py` — The Traffic Cop

When a message comes in:
1. Is it a text message? (ignore GPS, telemetry, etc.)
2. Is it a control command? (ban, warn, etc.)
3. What channel did it come from?
4. Find the right agent for that channel
5. Pass the message to the agent

Also handles rate limiting — one message per sender every 10 seconds.

### `agents/base.py` — The Claude API Call

**This is the important file.** The entire Claude interaction:

```python
# Create a client with your API key
self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

# Send a message
response = self.client.messages.create(
    model=self.model,                    # "claude-sonnet-4-5-20250929"
    max_tokens=self.max_tokens,          # 128 (short, for radio)
    system=system_prompt,                # "You are Sheila, a dry-witted..."
    messages=[{"role": "user", "content": message}],
)

# Get the text
text = response.content[0].text
```

Then it truncates to 220 bytes because LoRa can't handle more.

### `agents/conversational.py` — Custom Personality

Extends the base agent with a system prompt from `channels.yaml`. Also injects mesh radio context (signal strength, battery, hops) so Claude can reference it naturally in conversation.

### `agents/residue.py` — Memory Agent

Loads past interaction logs and weaves them into responses with simulated corruption — as if the AI's memory is degrading.

### `agents/ascii_visual.py` — ASCII Art Agent

Responds only in 5-line ASCII art patterns. No words, just visual.

### `control.py` — Admin Commands

Handles commands like `!ban`, `!warn`, `!persona`. Manages access control with three modes: admin-only, allowlist, or open (anarchy).

### `logger.py` — Logging

Saves every interaction to `logs/interactions.jsonl` with timestamps, sender info, channel, input, and output.

## The Flow for One Message

1. Someone on a Meshtastic radio types "what's the weather?" on channel 4
2. The radio sends it over LoRa → the Pi's Meshtastic device receives it
3. `main.py` gets the packet via the pub/sub listener
4. `router.py` sees it's channel 4 → that's Sheila (conversational agent)
5. `agents/conversational.py` builds the system prompt: "You are Sheila, dry-witted..."
6. `agents/base.py` sends it to Claude's API
7. Claude responds: "Check a window. I'm an AI on a radio, not a meteorologist."
8. `main.py` sends that back out over channel 4
9. The person sees it on their radio

## Key Takeaways

- The actual API call is ~10 lines of code
- Everything else is routing, rate limiting, logging, and personality
- The system prompt is what gives each agent its character
- Messages are capped at 220 bytes because of LoRa constraints
- The API key comes from an environment variable — never hardcoded
