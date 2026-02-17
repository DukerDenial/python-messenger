from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User
from ..auth import hash_password, create_access_token
from ..utils import save_file

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username==username).first()
    if user:
        return {"error": "User exists"}
    hashed = hash_password(password)
    user = User(username=username, password=hashed)
    db.add(user)
    db.commit()
    return {"success": True}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username==username).first()
    if not user:
        return {"error": "User not found"}
    from ..auth import verify_password
    if verify_password(password, user.password):
        token = create_access_token({"sub": user.username, "id": user.id})
        return {"token": token}
    return {"error": "Wrong password"}

@router.post("/avatar")
def upload_avatar(file: UploadFile, db: Session = Depends(get_db)):
    filename = save_file(file)
    # Привязка к пользователю пропускаем для простоты
    return {"filename": filename}
