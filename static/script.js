let socket = io();

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const data = await res.json();
    if (data.success) {
        alert("Registered successfully!");
    } else {
        alert(data.error);
    }
}

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const data = await res.json();

    if (data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("username", username);
        window.location.href = "/chat";
    } else {
        alert(data.error);
    }
}

if (window.location.pathname === "/chat") {
    const username = localStorage.getItem("username");
    socket.emit("join", {username});
}

socket.on("online_users", users => {
    const list = document.getElementById("onlineList");
    if (!list) return;

    list.innerHTML = "";
    users.forEach(user => {
        const li = document.createElement("li");
        li.textContent = user;
        list.appendChild(li);
    });
});

function send() {
    const sender = localStorage.getItem("username");
    const receiver = document.getElementById("receiver").value;
    const message = document.getElementById("msg").value;

    socket.emit("private_message", {sender, receiver, message});
}

socket.on("private_message", data => {
    const messages = document.getElementById("messages");
    if (!messages) return;

    const div = document.createElement("div");
    div.textContent = data.sender + ": " + data.message;
    messages.appendChild(div);
});

async function uploadAvatar() {
    const fileInput = document.getElementById("avatarUpload");
    const file = fileInput.files[0];

    if (!file) return;

    const form = new FormData();
    form.append("avatar", file);

    await fetch("/upload", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: form
    });

    alert("Avatar uploaded!");
}
