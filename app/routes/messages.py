# routes/messages.py

@router.post("/send")
def send_message(chat_id: int, content: str, user=Depends(get_current_user)):

    message = Message(
        content=content,
        sender_id=user.id,
        chat_id=chat_id,
        timestamp=datetime.utcnow()
    )

    db.add(message)
    db.commit()

    return {"status": "sent"}
