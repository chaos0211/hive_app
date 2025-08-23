from fastapi import APIRouter, HTTPException
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# 注册
@router.post("/register", response_model=UserOut)
def register(user: UserRegister):
    u = auth_service.register(user.username, user.password)
    if not u:
        raise HTTPException(status_code=400, detail="用户已存在")
    return u

# 登录
@router.post("/login", response_model=UserOut)
def login(user: UserLogin):
    u = auth_service.login(user.username, user.password)
    if not u:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return u
