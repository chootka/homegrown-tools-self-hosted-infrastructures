# Meshtastic MQTT Setup Guide

This guide walks through configuring Meshtastic devices to send and receive messages via an MQTT broker. All configuration is done through the Meshtastic mobile app.

## Overview

```
Meshtastic device → LoRa mesh → device with WiFi → MQTT broker → web app / other services
```

A Meshtastic device connected to WiFi acts as a **gateway** between the LoRa mesh and the internet. It publishes mesh messages to an MQTT broker (**uplink**) and can receive messages from MQTT and broadcast them to the mesh (**downlink**).

## What is MQTT?

MQTT is a lightweight messaging protocol. A **broker** (server) receives messages from **publishers** and forwards them to **subscribers** based on **topics** (like channels). Meshtastic uses MQTT to bridge the LoRa mesh to the internet.

## What is Uplink / Downlink?

- **Uplink**: mesh → MQTT. The device publishes messages it hears on the mesh to the MQTT broker.
- **Downlink**: MQTT → mesh. The device subscribes to MQTT topics and broadcasts incoming messages to the mesh.

## Prerequisites

- A Meshtastic device (e.g. Heltec ESP32, T-Beam)
- The Meshtastic mobile app (Android or iOS)
- A WiFi network the device can connect to
- An MQTT broker (e.g. Mosquitto running on a Raspberry Pi)

## Step 1: Connect to WiFi

In the Meshtastic app, connect to your device via Bluetooth, then:

1. Go to **Radio Configuration → Network**
2. Enable **WiFi**
3. Enter your WiFi **SSID** and **password**
4. Save — the device will reboot

## Step 2: Create Channels

You need two channels:

### Channel 0 (primary): `broadcasts`

This is the main channel where messages appear.

1. Go to **Channels**
2. Edit Channel 0
3. Set the name to `broadcasts` (or whatever you want your main channel to be called)
4. Enable **Uplink** (this publishes messages from this channel to MQTT)
5. Disable **Downlink**
6. Save

### Channel 1: `mqtt`

This is a dedicated channel for receiving messages from MQTT.

1. Add a new channel (Channel 1)
2. Set the name to `mqtt`
3. Disable **Uplink**
4. Enable **Downlink** (this subscribes to MQTT and broadcasts incoming messages to the mesh)
5. Save

### Primary vs Secondary Channels

Meshtastic supports up to 8 channels (0-7). **Channel 0 is always the primary channel** — you can only have one. It's the main channel the device uses for mesh communication. All other channels (1-7) are secondary. Think of it like a walkie-talkie: Channel 0 is the one you're always on, and the others are extra channels you can monitor at the same time. You cannot have more than one primary channel.

### Why two channels?

Messages published to the `mqtt` channel topic via MQTT will be received by devices with downlink enabled on that channel and broadcast to the mesh. They appear in the primary channel (`broadcasts`). This is how Meshtastic routes MQTT messages into the mesh.

## Step 3: Configure MQTT Module

Go to **Module Configuration → MQTT** and set:

| Setting | Value |
|---|---|
| Enabled | on |
| Server Address | your broker address (e.g. `dweb2025.nohost.me`) |
| Username | (empty, if anonymous access) |
| Password | (empty, if anonymous access) |
| Encryption Enabled | off |
| JSON Enabled | on |
| TLS Enabled | off |
| Root Topic | `msh/afterhours` (or your custom root topic) |
| Proxy to Client Enabled | off |

Save — the device will reboot.

### What do these settings mean?

- **JSON Enabled**: Publishes messages as human-readable JSON in addition to the default protobuf format. Required for our web app to read messages.
- **Encryption Enabled**: Encrypts MQTT payloads. Must be **off** for JSON mode to work, since JSON messages are not encrypted.
- **Root Topic**: The base of the MQTT topic tree. All messages are published under this path. Default is `msh/EU_868` (region-based), but a custom topic keeps your traffic separate.
- **Proxy to Client Enabled**: Routes MQTT traffic through a phone's internet connection. Not needed when the device has its own WiFi.
- **TLS Enabled**: Encrypts the connection to the MQTT broker. Not needed on a local/trusted network.

## Step 4: Configure LoRa Settings

Go to **Radio Configuration → LoRa** and check:

| Setting | Value |
|---|---|
| Ignore MQTT | false |
| OK to MQTT | true |

These settings control whether the device participates in MQTT integration.

## Step 5: Verify

### Test uplink (mesh → MQTT)

First, install the mosquitto client tools on your laptop:

**Mac:**
```bash
brew install mosquitto
```

**Windows** (using Chocolatey):
```
choco install mosquitto
```

Or download the installer from https://mosquitto.org/download/

Then subscribe to all messages on the broker:

```bash
mosquitto_sub -h dweb2025.nohost.me -p 1883 -t 'msh/afterhours/#' -v
```

Send a message from the Meshtastic app on the `broadcasts` channel. You should see it appear in the terminal as JSON.

### Understand the topic structure

Meshtastic publishes to two topic formats:

```
{root_topic}/2/e/{channel_name}/{node_id}      ← protobuf (binary)
{root_topic}/2/json/{channel_name}/{node_id}    ← JSON (readable)
```

For example:
```
msh/afterhours/2/json/broadcasts/!9e761674
```

A JSON message looks like:
```json
{
  "channel": 0,
  "from": 2658539124,
  "hop_start": 3,
  "hops_away": 0,
  "id": 3365877190,
  "payload": {
    "text": "hello from the mesh"
  },
  "sender": "!9e761674",
  "timestamp": 1773752906,
  "to": 4294967295,
  "type": "text"
}
```

### Message types you'll see

| Type | Description |
|---|---|
| `text` | A text message sent by a user |
| `nodeinfo` | Device info (name, hardware, role) |
| `position` | GPS coordinates |
| `telemetry` | Battery, voltage, temperature, etc. |

## Sending Messages to the Mesh via MQTT (Downlink)

> **Status: TBD** — downlink configuration is still being tested. The broker successfully delivers messages to the devices, but the devices are not yet broadcasting them to the mesh. This section will be updated once the issue is resolved.

### Expected Setup

With the channel configuration above (channel 1 `mqtt` with downlink enabled), you should be able to publish a message to the MQTT broker that gets broadcast to the mesh:

```bash
mosquitto_pub -h dweb2025.nohost.me -p 1883 \
  -t 'msh/afterhours/2/json/mqtt/!<node_id>' \
  -m '{"from": <node_decimal_id>, "type": "sendtext", "payload": "hello from mqtt"}'
```

The message should appear in the `broadcasts` channel on all devices on the mesh.

### Converting Node IDs

The node ID (e.g. `!9e761674`) is hexadecimal. The `from` field in JSON needs the decimal equivalent:

- `!9e761674` → `0x9e761674` → `2658539124`
- `!a6965508` → `0xa6965508` → `2794870024`

You can convert in Python: `int("9e761674", 16)`

## Notes

- **Only one program can use the serial port at a time.** If you're connected to a device via USB serial, disconnect before using Bluetooth.
- **Close the Meshtastic app** if you want another phone to connect to a device via Bluetooth — only one Bluetooth connection at a time.
- **Multiple devices with uplink enabled** will publish the same message to the broker multiple times (once per device that hears it over LoRa). Deduplicate by message `id` on the receiving end.
- **TX Power**: If using a high-gain antenna (e.g. 6 dBi), reduce TX power to stay within local regulations. For EU 868 MHz with a 6 dBi antenna, set TX power to 8 dBm (8 + 6 = 14 dBm ERP, within the 25 mW limit).

## Troubleshooting

| Problem | Fix |
|---|---|
| Device not connecting to MQTT broker | Check WiFi is connected, verify broker address, check port 1883 is open |
| No messages appearing in MQTT | Make sure JSON Enabled is on, uplink is enabled on the channel |
| Duplicate messages | Multiple devices uplinking the same message — deduplicate by message `id` |
| "Connection refused" from mosquitto tools | Check broker is running, port is open, firewall allows 1883 |
| Downlink not working | TBD — still debugging |
