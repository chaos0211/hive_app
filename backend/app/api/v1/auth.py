from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.services import auth_service
from app.services.auth_service import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    u = auth_service.register(db, user.username, user.password)
    if not u:
        raise HTTPException(status_code=400, detail="用户已存在")
    return u

@router.post("/login", response_model=UserOut)
def login(user: UserLogin, db: Session = Depends(get_db)):
    u = auth_service.login(db, user.username, user.password)
    if not u:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return u

