let socket = io();
let token = localStorage.getItem("token");
let username = "";

async function register() {
    await fetch("/register", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            username:username.value,
            password:password.value
        })
    });
    alert("Registered");
}

async function login() {
    const res = await fetch("/login", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            username:username.value,
            password:password.value
        })
    });

    const data = await res.json();
    localStorage.setItem("token", data.token);
    localStorage.setItem("username", username.value);
    window.location="/chat";
}

if(window.location.pathname==="/chat"){
    username = localStorage.getItem("username");
    socket.emit("join",{username:username});
}

socket.on("online_users", users=>{
    onlineList.innerHTML="";
    users.forEach(u=>{
        let li=document.createElement("li");
        li.textContent=u;
        onlineList.appendChild(li);
    });
});

function send(){
    socket.emit("private_message",{
        sender:username,
        receiver:receiver.value,
        message:msg.value
    });
}

socket.on("private_message",data=>{
    let div=document.createElement("div");
    div.textContent=data.sender+": "+data.message;
    messages.appendChild(div);
});

async function uploadAvatar(){
    let file=document.getElementById("avatarUpload").files[0];
    let form=new FormData();
    form.append("avatar",file);

    await fetch("/upload",{
        method:"POST",
        headers:{Authorization:"Bearer "+localStorage.getItem("token")},
        body:form
    });

    alert("Avatar uploaded");
}
