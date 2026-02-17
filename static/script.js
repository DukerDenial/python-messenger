let socket = io();
let currentChat = null;
let username = localStorage.getItem("username");

document.getElementById("myName").textContent = username;

socket.emit("join", {username});

socket.on("online_users", users => {
    const list = document.getElementById("dialogList");
    list.innerHTML = "";

    users.forEach(user => {
        if (user === username) return;

        let li = document.createElement("li");
        li.className = "dialog-item";
        li.innerHTML = `
            <img src="/avatar/${user}.png" class="avatar">
            <span>${user}</span>
        `;
        li.onclick = () => openChat(user);
        list.appendChild(li);
    });
});

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/register", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });

    const data = await res.json();

    if(data.success){
        login();
    } else {
        document.getElementById("authError").textContent = data.error;
    }
}

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/login", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username,password})
    });

    const data = await res.json();

    if(data.token){
        localStorage.setItem("token", data.token);
        localStorage.setItem("username", username);
        window.location="/chat";
    } else {
        document.getElementById("authError").textContent = data.error;
    }
}


function openChat(user) {
    currentChat = user;
    document.getElementById("chatName").textContent = user;
    document.getElementById("chatAvatar").src = `/avatar/${user}.png`;
    document.getElementById("chatStatus").textContent = "online";
    document.getElementById("messages").innerHTML = "";
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value;

    if (!message || !currentChat) return;

    socket.emit("private_message", {
        sender: username,
        receiver: currentChat,
        message: message
    });

    input.value = "";
}

socket.on("private_message", data => {
    if (data.sender === currentChat) {
        addMessage("other", data.message);
    }
});

function addMessage(type, text) {
    const div = document.createElement("div");
    div.className = "message " + type;
    div.textContent = text;
    document.getElementById("messages").appendChild(div);
}
