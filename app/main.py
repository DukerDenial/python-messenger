from fastapi import FastAPI
from app.routes import users, chats, messages
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Messenger PRO")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в проде указывай фронтенд домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(chats.router, prefix="/chats", tags=["Chats"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
