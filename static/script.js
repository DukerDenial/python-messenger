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

    addMessage("me", message);
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
