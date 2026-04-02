# Student Setup Guide: Local LLM + Meshtastic + MQTT

A complete guide to setting up your own AI agent ecosystem on a Raspberry Pi. This guide assumes you're starting from zero and walks through every step.

## What You're Building

Your own AI agent that:
- Listens for radio messages on a Meshtastic channel
- Generates responses using a local LLM running on your Pi (no cloud, no API key)
- Sends responses back over radio
- Can control a shared website via MQTT

Everything runs on your Raspberry Pi. The only external service is the shared MQTT broker for the website.

---

## What You Need

Before starting, make sure you have all of these:

| Item | Notes |
|---|---|
| Raspberry Pi 5 (4GB or 8GB) | Must be set up with Raspberry Pi OS and SSH access |
| 2x Meshtastic devices | One plugs into Pi (USB), one pairs with phone (Bluetooth) |
| USB data cable | **Not** charge-only — must carry data. If in doubt, try a different cable |
| Phone with Meshtastic app | Android or iOS — download from app store |
| Laptop | To SSH into your Pi |
| Internet connection | Your Pi needs internet for initial setup and MQTT. Ollama works offline after setup |

---

## The Full Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         YOUR SETUP (per student)                        │
│                                                                         │
│  ┌──────────────┐         ┌──────────────────────────────────────────┐  │
│  │              │         │  YOUR RASPBERRY PI                       │  │
│  │  Your Phone  │         │  (e.g. 192.168.x.x on local network)    │  │
│  │  Meshtastic  │         │                                          │  │
│  │  App         │         │  ┌────────────────────────────────────┐  │  │
│  │              │         │  │  Ollama (http://localhost:11434)   │  │  │
│  └──────┬───────┘         │  │  Model: tinyllama or llama3.2:3b  │  │  │
│         │                 │  │  Runs 100% locally, no internet   │  │  │
│    Bluetooth              │  └──────────────────┬─────────────────┘  │  │
│         │                 │                     │                     │  │
│         ▼                 │                     │ HTTP API            │  │
│  ┌──────────────┐  USB    │                     │ (localhost:11434)   │  │
│  │  Meshtastic  │ serial  │                     │                     │  │
│  │  Device #2   ├─────────┤                     │                     │  │
│  │  (on phone)  │         │  ┌──────────────────┴─────────────────┐  │  │
│  └──────────────┘         │  │  Channels App (main_ollama.py)    │  │  │
│         ▲                 │  │                                    │  │  │
│         │                 │  │  • Receives radio msgs over USB   │  │  │
│      LoRa radio           │  │  • Routes to the right agent      │  │  │
│    (868 MHz)              │  │  • Agent asks Ollama for response  │  │  │
│         │                 │  │  • Sends response back over radio  │  │  │
│         ▼                 │  │  • Webmistress publishes to MQTT  │  │  │
│  ┌──────────────┐  USB    │  │                                    │  │  │
│  │  Meshtastic  │ serial  │  └──────────────────┬─────────────────┘  │  │
│  │  Device #1   ├─────────┤                     │                     │  │
│  │  (on Pi)     │         │                MQTT publish               │  │
│  └──────────────┘         │           (port 1883, internet)           │  │
│                           └─────────────────────┬────────────────────┘  │
└─────────────────────────────────────────────────┼───────────────────────┘
                                                  │
                                            internet
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHARED INFRASTRUCTURE (instructor's Pi)               │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  RASPBERRY PI: dweb2025.nohost.me                                │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────┐  ┌────────────────────────────────┐ │  │
│  │  │  Mosquitto MQTT Broker  │  │  Mesh Web App (Flask)          │ │  │
│  │  │  Port: 1883             │  │  Port: 5002 (behind nginx)     │ │  │
│  │  │  No auth required       │  │                                │ │  │
│  │  │                         │  │  Subscribes to MQTT            │ │  │
│  │  │  Receives commands from │  │  Displays messages             │ │  │
│  │  │  student Pis            │  │  Reacts to commands:           │ │  │
│  │  │                         │  │  blue, red, purple, stripes,   │ │  │
│  │  └────────────┬────────────┘  │  hide, show, rotate, reset     │ │  │
│  │               │               │                                │ │  │
│  │               └──────────────►│  ← reads commands from MQTT    │ │  │
│  │                               │                                │ │  │
│  │                               └────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Website visible at: https://mqtt.dweb2025.nohost.me                    │
│  MQTT broker at: dweb2025.nohost.me:1883                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What Runs Where

| Component | Where it runs | Address | Internet needed? |
|---|---|---|---|
| Ollama (LLM) | Your Pi | `localhost:11434` | No (after initial model download) |
| Channels app | Your Pi | runs locally | No (except for MQTT publish) |
| Meshtastic device | USB on your Pi | `/dev/ttyUSB0` or `/dev/ttyACM0` | No |
| MQTT broker | Instructor's Pi | `dweb2025.nohost.me:1883` | Yes (to publish) |
| Website | Instructor's Pi | `https://mqtt.dweb2025.nohost.me` | Yes (to view) |

---

## Step-by-Step Setup

### Step 0: Prerequisites — Check Your Pi

SSH into your Pi from your laptop:

```bash
ssh your-username@your-pi-address
```

If you don't know your Pi's address, check your router's device list or try `raspberrypi.local`.

Once logged in, verify you have the basics:

```bash
# Check Python is installed
python3 --version
# Should show Python 3.x — if not: sudo apt install python3

# Check pip is installed
pip3 --version
# If not: sudo apt install python3-pip

# Check git is installed
git --version
# If not: sudo apt install git

# Check you have venv support
python3 -m venv --help
# If not: sudo apt install python3-venv
```

**Before moving on, confirm:** You can SSH in and `python3 --version` returns 3.x.

---

### Step 1: Install Ollama

Ollama runs LLMs locally on your Pi. Install it:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This takes a few minutes. When it's done, verify:

```bash
ollama --version
```

Now download a model. For 4GB Pi use `tinyllama`, for 8GB Pi use `llama3.2:3b`:

```bash
# 4GB Pi:
ollama pull tinyllama

# 8GB Pi (better quality):
ollama pull llama3.2:3b
```

This downloads the model file (~1-2 GB). One-time download — after this, no internet needed to use it.

Test it:

```bash
ollama run tinyllama "What is a mesh network? Answer in one sentence."
```

It will take a few seconds — that's normal on a Pi. You should see a response.

**Before moving on, confirm:** `ollama run tinyllama "hello"` returns a response.

---

### Step 2: Plug in Your Meshtastic Device

Connect one Meshtastic device to your Pi via USB. This is the device the channels app will use to send and receive radio messages.

Check it's detected:

```bash
ls /dev/ttyUSB*
```

If nothing, try:

```bash
ls /dev/ttyACM*
```

You should see something like `/dev/ttyUSB0` or `/dev/ttyACM0`. If nothing shows up:
- Try a different USB port on the Pi
- Try a different cable — many USB-C cables are charge-only with no data
- Unplug and replug

**Before moving on, confirm:** `ls /dev/ttyUSB*` or `ls /dev/ttyACM*` shows a device.

---

### Step 3: Configure Meshtastic Channels

Your Meshtastic device needs channels that match the channels app. The **index number** is what matters — the app routes messages by channel index.

Open the Meshtastic app on your phone. Connect to your **other** Meshtastic device (the one NOT plugged into the Pi) via Bluetooth.

#### Add channels:

Go to **Channels** in the Meshtastic app. You should see your existing channels (probably channel 0). You need to add new channels at specific indices.

For each channel below, tap **Add Channel** (or the + button):

| Index | Name | Notes |
|---|---|---|
| 3 | sysop | Admin agent — BBS-style operator |
| 4 | sheila | Conversational agent — sarcastic helper |
| 5 | webmistress | Controls the shared website via MQTT |
| 6 | lowviz | ASCII art agent — responds in patterns only |
| 7 | mmmmmmorse | Morse code translator |

For each channel:
1. Set the **name** as shown above
2. Leave **PSK** as default (`AQ==`) or empty — just make sure both devices use the same setting
3. **Uplink/Downlink** — leave off, not needed
4. **Save**

**Important:** Keep your existing channels (0, 1, etc.) — don't delete them. Just add the new ones.

You also need the same channels on the device plugged into the Pi. The easiest way: connect to that device via Bluetooth temporarily, add the same channels, then disconnect and plug it back into the Pi via USB.

**Before moving on, confirm:** Both Meshtastic devices have channels 3-7 configured. You can verify by opening the Meshtastic app and checking the channel list on each device.

---

### Step 4: Clone and Set Up the Channels App

On your Pi (via SSH):

```bash
cd ~
git clone https://github.com/chootka/channels.git
cd channels
```

Create a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This installs everything the app needs: the Meshtastic library, MQTT client, YAML parser, etc.

**Before moving on, confirm:** `pip list` shows `meshtastic`, `paho-mqtt`, `pyyaml`, and `requests` installed.

---

### Step 5: Create the `.env` Configuration File

The `.env` file tells the app where to find the MQTT broker and which channel config to use.

```bash
cd ~/channels
nano .env
```

Add these lines:

```
MQTT_BROKER=dweb2025.nohost.me
MQTT_PORT=1883
CHANNELS_FILE=channels_ollama.yaml
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

No API key is needed — we're using local Ollama, not Claude.

**Before moving on, confirm:** `cat .env` shows the three lines above.

---

### Step 6: Run the Channels App

Make sure your Meshtastic device is plugged into the Pi via USB, then:

```bash
cd ~/channels
source venv/bin/activate
python main_ollama.py
```

You should see:

```
[router] Loaded 5 channels: 3=sysop, 4=sheila, 5=webmistress, 6=lowviz, 7=mmmmmmorse
[main] Connecting to Meshtastic device...
[main] Using LOCAL Ollama — no internet or API key needed.
[main] Listening for messages. Ctrl+C to quit.
```

If you see an error about the serial port, try specifying it in your `.env`:

```
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

(Use whatever path you found in Step 2.)

**Before moving on, confirm:** The app is running and says "Listening for messages."

---

### Step 7: Test It

From your phone's Meshtastic app (connected to the other device via Bluetooth):

#### Test sheila (channel 4):
1. Open channel 4 (sheila) in the Meshtastic app
2. Type a message: "hello"
3. Wait 5-15 seconds (Ollama needs time to generate on the Pi)
4. You should see a response appear in the Meshtastic app
5. In the SSH terminal, you should see the message and response logged

#### Test webmistress (channel 5):
1. Open channel 5 (webmistress) in the Meshtastic app
2. Type: "make it blue"
3. Check the website at `https://mqtt.dweb2025.nohost.me` — the background should change
4. Try: "rotate", "hide", "stripes", "reset"

**If sheila doesn't respond:**
- Check the terminal for errors
- Is Ollama running? Try `ollama run tinyllama "test"` in another SSH session
- Is the channel index correct? The app expects sheila on index 4

**If the website doesn't change:**
- Can your Pi reach the MQTT broker? Try: `mosquitto_pub -h dweb2025.nohost.me -p 1883 -t 'test' -m 'hello'`
- If that fails, check your internet connection

---

## The Message Flow

### When someone talks to an agent (e.g. sheila on channel 4):

```
1. You type "hello" in the Meshtastic app on your phone
       │
2.     └──► Phone sends via Bluetooth to Meshtastic device #2
                 │
3.               └──► Device #2 transmits over LoRa radio (868 MHz)
                           │
4.                         └──► Meshtastic device #1 (on Pi) receives it
                                     │
5.                                   └──► USB serial to your Pi
                                               │
6.                                             └──► Channels app (main_ollama.py)
                                                         │
7.                                                       └──► Router → channel 4 → sheila agent
                                                                   │
8.                                                                 └──► Ollama (localhost:11434)
                                                                             │
9.                                                                  Generates response locally
                                                                             │
10.                                                                ┌────────┘
                                                                   │
11.                              Channels app sends response back ◄┘
                                         │
12.                                      └──► USB serial → device #1 → LoRa → device #2
                                                                                    │
13.                                                                    Bluetooth → your phone
                                                                                    │
14.                                                              You see the reply ◄┘
```

### When someone talks to webmistress (channel 5):

Same flow as above, plus one extra step after the response is generated:

```
The agent also publishes the command to MQTT:

    agent ──► MQTT publish ──► dweb2025.nohost.me:1883
                                         │
                                         └──► Web app receives it
                                                   │
                                                   └──► Website changes
                                                        (everyone watching sees it)
```

---

## Restarting Everything

When you come back to your Pi later (next class, next day, etc.), here's how to get everything running again.

### 1. SSH into your Pi

```bash
ssh your-username@your-pi-address
```

### 2. Check Ollama is running

```bash
ollama run tinyllama "test"
```

If it says "connection refused", start Ollama:

```bash
ollama serve &
```

### 3. Make sure the Meshtastic device is plugged in

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

### 4. Start the channels app

```bash
cd ~/channels
source venv/bin/activate
python main_ollama.py
```

That's it. Three commands and you're back up.

---

## Ports Reference

```
YOUR PI:
  11434  ← Ollama HTTP API (localhost only, no internet needed)
  USB    ← Meshtastic serial connection (/dev/ttyUSB0 or /dev/ttyACM0)

INSTRUCTOR'S PI (dweb2025.nohost.me):
  1883   ← MQTT broker (Mosquitto) — accepts connections from student Pis
  443    ← Website HTTPS (nginx → Flask on port 5002)
```

---

## Available Agents

| Channel | Agent | What it does | Example |
|---|---|---|---|
| 3 | sysop | Admin commands, talks like a '90s BBS operator | "!status" |
| 4 | sheila | Sarcastic but helpful conversational assistant | "What is TCP?" |
| 5 | webmistress | Controls the website — responds with commands | "make it purple" |
| 6 | lowviz | Responds only in 5-line ASCII art patterns | "hello" → art pattern |
| 7 | mmmmmmorse | Translates to/from Morse code | "hello" → ".... . .-.. .-.. ---" |

### Webmistress commands

The webmistress agent understands natural language and translates it to one of these commands:

| Say something like... | Command sent | Effect on website |
|---|---|---|
| "make it blue" / "blue background" | `blue` | Background turns dark blue |
| "turn it red" | `red` | Background turns dark red |
| "purple please" | `purple` | Background turns dark purple |
| "add stripes" | `stripes` | Diagonal stripe pattern |
| "hide everything" / "redact it" | `hide` | All text gets redacted (black boxes) |
| "show the text" / "un-redact" | `show` | Text becomes visible again |
| "spin the page" / "make it rotate" | `rotate` | Page slowly rotates |
| "reset everything" / "back to normal" | `reset` | Undo all effects |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Can't SSH into Pi | Check Pi is powered on and connected to the same network. Try `ping your-pi-address` |
| `python3: command not found` | `sudo apt install python3` |
| `pip3: command not found` | `sudo apt install python3-pip` |
| `venv: command not found` | `sudo apt install python3-venv` |
| `ollama: command not found` | Install: `curl -fsSL https://ollama.com/install.sh \| sh` |
| `ollama run` says connection refused | Start Ollama: `ollama serve &` |
| Ollama is very slow | Normal on Pi — responses take 5-15 seconds with tinyllama |
| No serial device found (`/dev/ttyUSB*`) | Try different USB port, try different cable (must be data cable) |
| `Meshtastic serial port disconnected` | Unplug and replug USB, restart the channels app |
| Agent doesn't respond to messages | Check channel index matches config. Check terminal for errors |
| `Connection refused` on MQTT | Check Pi has internet. Try: `ping dweb2025.nohost.me` |
| Website doesn't change | Is MQTT broker online? Is the web app running? Ask instructor |
| Phone can't connect to Meshtastic via Bluetooth | Make sure the device isn't connected to another phone. Only one Bluetooth connection at a time |
| Wrong channel — message not picked up | The channel **index** must match (3-7). Check in the Meshtastic app |

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│              QUICK REFERENCE                      │
│                                                  │
│  SSH into Pi:                                    │
│    ssh your-username@your-pi-address             │
│                                                  │
│  Start Ollama:                                   │
│    ollama serve &                                │
│                                                  │
│  Start channels app:                             │
│    cd ~/channels                                 │
│    source venv/bin/activate                      │
│    python main_ollama.py                         │
│                                                  │
│  Check Meshtastic USB:                           │
│    ls /dev/ttyUSB* /dev/ttyACM*                  │
│                                                  │
│  Test Ollama:                                    │
│    ollama run tinyllama "hello"                  │
│                                                  │
│  Test MQTT:                                      │
│    mosquitto_pub -h dweb2025.nohost.me \         │
│      -p 1883 -t 'test' -m 'hello'               │
│                                                  │
│  Website:                                        │
│    https://mqtt.dweb2025.nohost.me               │
│                                                  │
│  Channels:                                       │
│    3=sysop  4=sheila  5=webmistress             │
│    6=lowviz  7=mmmmmmorse                        │
│                                                  │
│  Stop the app:                                   │
│    Ctrl+C                                        │
└──────────────────────────────────────────────────┘
```
