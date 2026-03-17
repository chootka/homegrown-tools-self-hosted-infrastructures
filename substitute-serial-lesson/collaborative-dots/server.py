from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "collaborative-dots"
socketio = SocketIO(app, cors_allowed_origins="*")

# Connected clients: { sid: { name, color, x, y } }
clients = {}

NAMES = [
    "Maple", "Fern", "Basil", "Clover", "Sage", "Olive", "Hazel",
    "Juniper", "Cedar", "Willow", "Iris", "Dahlia", "Aster", "Moss",
    "Reed", "Linden", "Sorrel", "Yarrow", "Briar", "Wren",
    "Finch", "Lark", "Robin", "Sparrow", "Cricket",
]

COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
    "#F1948A", "#82E0AA", "#F8C471", "#AED6F1", "#D2B4DE",
    "#A3E4D7", "#FAD7A0", "#A9CCE3", "#D5DBDB", "#F5B7B1",
]


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    name = random.choice(NAMES)
    color = random.choice(COLORS)
    clients[__import__("flask").request.sid] = {
        "name": name,
        "color": color,
        "x": 0.5,
        "y": 0.5,
    }
    emit("assigned", {"name": name, "color": color})
    emit("all_positions", clients, broadcast=True)
    print(f"+ {name} connected ({len(clients)} total)")


@socketio.on("disconnect")
def handle_disconnect():
    sid = __import__("flask").request.sid
    if sid in clients:
        name = clients[sid]["name"]
        del clients[sid]
        emit("all_positions", clients, broadcast=True)
        print(f"- {name} disconnected ({len(clients)} total)")


@socketio.on("position")
def handle_position(data):
    sid = __import__("flask").request.sid
    if sid in clients:
        clients[sid]["x"] = data["x"]
        clients[sid]["y"] = data["y"]
        emit("all_positions", clients, broadcast=True)


if __name__ == "__main__":
    print("Server running on http://0.0.0.0:8080")
    print("Students should open http://<your-ip>:8080 in Chrome")
    socketio.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
