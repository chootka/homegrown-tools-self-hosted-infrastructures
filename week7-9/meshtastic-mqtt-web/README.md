# Meshtastic MQTT to Web

A simple web app that displays live messages from a Meshtastic mesh network via MQTT.

## How It Works

```
Meshtastic devices → LoRa mesh → MQTT broker → Python app → Web browser
```

1. Meshtastic devices send messages on the mesh
2. Devices with WiFi + MQTT enabled publish messages to the MQTT broker
3. A Python Flask app subscribes to the MQTT topic
4. Messages are pushed to the browser in real time via Server-Sent Events (SSE)

## Setup

### Requirements

- Python 3
- A Meshtastic device with WiFi access
- An MQTT broker (we use Mosquitto on a Raspberry Pi)

### Install and Run

```bash
cd meshtastic-mqtt-web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5001 in your browser.

### Configuration

Edit the top of `app.py` to match your setup:

```python
MQTT_BROKER = "dweb2025.nohost.me"   # Your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC = "msh/afterhours/2/json/broadcasts/#"  # Must match your root topic and channel
```

## Meshtastic Device Configuration

Each device needs the following settings configured via the Meshtastic mobile app:

### MQTT Module

| Setting | Value |
|---|---|
| Enabled | on |
| Server Address | `dweb2025.nohost.me` |
| Username | (empty) |
| Password | (empty) |
| Encryption Enabled | off |
| JSON Enabled | on |
| TLS Enabled | off |
| Root Topic | `msh/afterhours` |
| Proxy to Client Enabled | off |

### Channels

| Channel | Name | Uplink | Downlink |
|---|---|---|---|
| 0 | `broadcasts` | on | off |
| 1 | `mqtt` | off | on |

### Other Settings

| Setting | Value |
|---|---|
| Region | EU_868 |
| Role | CLIENT |
| TX Power | 8 dBm (for use with 6 dBi antenna, EU compliant) |
| Network / WiFi | enabled, connected to local WiFi |
| LoRa / Ignore MQTT | false |
| LoRa / OK to MQTT | true |

## Testing

### Verify MQTT broker connectivity

```bash
brew install mosquitto
mosquitto_sub -h dweb2025.nohost.me -p 1883 -t 'msh/afterhours/#' -v
```

Send a message from a Meshtastic device — you should see it appear in the terminal.

### Verify the web app

With the Python app running, open http://localhost:5001 and send a message from a Meshtastic device. It should appear on the page.

## MQTT Topic Structure

Meshtastic uses this topic format:

```
{root_topic}/2/e/{channel_name}/{node_id}     ← protobuf (encrypted)
{root_topic}/2/json/{channel_name}/{node_id}  ← JSON (readable)
```

For our setup:
```
msh/afterhours/2/json/broadcasts/!a6965508    ← JSON message from node !a6965508
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Python app can't connect to broker | Check broker address and that port 1883 is open |
| No messages appearing | Make sure JSON Enabled is on in MQTT settings |
| Web page says "connecting..." | Make sure the app is running on port 5001 |
| "Port 5000 in use" | macOS AirPlay uses 5000, app uses 5001 instead |
| Device not connecting to MQTT | Check WiFi is enabled and connected on the device |
