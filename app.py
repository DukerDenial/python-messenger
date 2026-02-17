import os
import bcrypt
import sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret"
app.config["JWT_SECRET_KEY"] = "jwt-secret"
app.config["UPLOAD_FOLDER"] = "uploads"

jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ---------- DATABASE ----------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    avatar TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    message TEXT
)
""")

conn.commit()

online_users = {}

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                       (username, password))
        conn.commit()
        return jsonify(success=True)
    except:
        return jsonify(error="User exists"), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    cursor.execute("SELECT password FROM users WHERE username=?",
                   (data["username"],))
    user = cursor.fetchone()

    if not user:
        return jsonify(error="User not found"), 400

    if bcrypt.checkpw(data["password"].encode(), user[0]):
        token = create_access_token(identity=data["username"])
        return jsonify(token=token)

    return jsonify(error="Wrong password"), 400

@app.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    user = get_jwt_identity()
    file = request.files["avatar"]
    filename = user + ".png"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    cursor.execute("UPDATE users SET avatar=? WHERE username=?",
                   (filename, user))
    conn.commit()

    return jsonify(success=True)

@app.route("/avatar/<filename>")
def avatar(filename):
    return send_from_directory("uploads", filename)

# ---------- SOCKET ----------
@socketio.on("connect")
def connect():
    print("User connected")

@socketio.on("join")
def on_join(data):
    username = data["username"]
    online_users[username] = request.sid
    emit("online_users", list(online_users.keys()), broadcast=True)

@socketio.on("private_message")
def handle_private(data):
    sender = data["sender"]
    receiver = data["receiver"]
    message = data["message"]

    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?,?,?)",
                   (sender, receiver, message))
    conn.commit()

    if receiver in online_users:
        emit("private_message", data, room=online_users[receiver])

@socketio.on("disconnect")
def disconnect():
    for user, sid in list(online_users.items()):
        if sid == request.sid:
            del online_users[user]
    emit("online_users", list(online_users.keys()), broadcast=True)

# ---------- RUN ----------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
    

