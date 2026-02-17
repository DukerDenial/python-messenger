import os
import sqlite3
import bcrypt
import random
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

DEFAULT_AVATARS = [
    "default1.png",
    "default2.png",
    "default3.png"
]

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret"
app.config["JWT_SECRET_KEY"] = "jwt-secret"
app.config["UPLOAD_FOLDER"] = "uploads"

socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

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
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    default_avatar = random.choice(DEFAULT_AVATARS)

    try:
        cursor.execute(
            "INSERT INTO users (username, password, avatar) VALUES (?,?,?)",
            (username, hashed, default_avatar)
        )
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    cursor.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 400

    if bcrypt.checkpw(password.encode(), user[0].encode()):
        token = create_access_token(identity=username)
        return jsonify({"token": token})

    return jsonify({"error": "Wrong password"}), 400


@app.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    current_user = get_jwt_identity()
    file = request.files.get("avatar")

    if not file:
        return jsonify({"error": "No file"}), 400

    filename = f"{current_user}.png"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    cursor.execute(
        "UPDATE users SET avatar=? WHERE username=?",
        (filename, current_user)
    )
    conn.commit()

    return jsonify({"success": True})


@app.route("/avatar/<filename>")
def avatar(filename):
    return send_from_directory("uploads", filename)


# ---------- SOCKET ----------

@socketio.on("join")
def join(data):
    username = data["username"]
    online_users[username] = request.sid
    emit("online_users", list(online_users.keys()), broadcast=True)


@socketio.on("private_message")
def private_message(data):
    sender = data["sender"]
    receiver = data["receiver"]
    message = data["message"]

    cursor.execute(
        "INSERT INTO messages (sender, receiver, message) VALUES (?,?,?)",
        (sender, receiver, message)
    )
    conn.commit()

    # Отправить получателю
    if receiver in online_users:
        emit("private_message", data, room=online_users[receiver])

    # Отправить отправителю (чтобы отобразилось)
    emit("private_message", data, room=online_users[sender])



@socketio.on("disconnect")
def disconnect():
    for user, sid in list(online_users.items()):
        if sid == request.sid:
            del online_users[user]
    emit("online_users", list(online_users.keys()), broadcast=True)


# ---------- RUN ----------

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
