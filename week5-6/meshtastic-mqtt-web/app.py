import json
import queue
import threading
from flask import Flask, Response, render_template
import paho.mqtt.client as mqtt

# ---- Configuration ----
MQTT_BROKER = "dweb2025.nohost.me"
MQTT_PORT = 1883
MQTT_TOPIC = "msh/EU_868/2/json/afterhours/#"

app = Flask(__name__)

# Thread-safe queue to pass messages from MQTT thread to SSE clients
listeners = []
listeners_lock = threading.Lock()


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

    message = {
        "topic": msg.topic,
        "from": payload.get("from"),
        "to": payload.get("to"),
        "type": payload.get("type"),
        "payload": payload.get("payload"),
        "timestamp": payload.get("timestamp"),
    }

    print(f"Message: {message}")
    broadcast(message)


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
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

    print("Starting web server on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, threaded=True)
