from fastapi import WebSocket
from typing import Dict

connections: Dict[int, WebSocket] = {}

async def connect_user(user_id: int, websocket: WebSocket):
    await websocket.accept()
    connections[user_id] = websocket

async def disconnect_user(user_id: int):
    if user_id in connections:
        del connections[user_id]

async def send_message(user_id: int, data: dict):
    if user_id in connections:
        await connections[user_id].send_json(data)
