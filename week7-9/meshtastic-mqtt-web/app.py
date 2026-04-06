import json
import os
import queue
import threading
from dotenv import load_dotenv
from flask import Flask, Response, render_template
import paho.mqtt.client as mqtt

load_dotenv()

# ---- Configuration ----
MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt.meshtastic.org")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "meshdev")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "large4cats")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "msh/afterhours/2/json/broadcasts/#")
WEB_PORT = int(os.environ.get("WEB_PORT", "5001"))

app = Flask(__name__)

# Thread-safe queue to pass messages from MQTT thread to SSE clients
listeners = []
listeners_lock = threading.Lock()

# Deduplication: track recently seen message IDs
seen_ids = set()
MAX_SEEN = 500


def broadcast(data):
    """Send a message to all connected SSE clients."""
    with listeners_lock:
        dead = []
        for q in listeners:
            try:
                q.put_nowait(data)
            except queue.Full:
                dead.append(q)
        for q in dead:
            listeners.remove(q)


# ---- MQTT ----
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker, subscribing to {MQTT_TOPIC}")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Skip non-JSON messages (encrypted protobuf packets)
        return

    # Deduplicate — both devices uplink the same message
    msg_id = payload.get("id")
    if msg_id is not None:
        if msg_id in seen_ids:
            return
        seen_ids.add(msg_id)
        if len(seen_ids) > MAX_SEEN:
            seen_ids.clear()

    message = {
        "topic": msg.topic,
        "from": payload.get("from"),
        "to": payload.get("to"),
        "type": payload.get("type"),
        "payload": payload.get("payload"),
        "timestamp": payload.get("timestamp"),
        "sender": payload.get("sender"),
    }

    print(f"Message: {message}")
    broadcast(message)


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


# ---- Web Routes ----
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stream")
def stream():
    """SSE endpoint — browser connects here to receive live messages."""
    q = queue.Queue(maxsize=50)
    with listeners_lock:
        listeners.append(q)

    def generate():
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            with listeners_lock:
                if q in listeners:
                    listeners.remove(q)

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    # Start MQTT in a background thread
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()

    print(f"Starting web server on http://localhost:{WEB_PORT}")
    app.run(host="0.0.0.0", port=WEB_PORT, threaded=True)
