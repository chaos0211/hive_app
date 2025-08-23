
# 1. 创建目录
mkdir -p backend/app/{api/v1,core,schemas,services,db/models}

# 2. requirements
cat > backend/requirements.txt <<'REQ'
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.8.2
REQ

# 3. main.py
cat > backend/app/main.py <<'PY'
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, analytics

app = FastAPI(title="Huawei App Dashboard API", version="0.1.0")

# 允许前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(analytics.router)

@app.get("/health")
def health():
    return {"status": "ok"}
PY

# 4. schemas/user.py
cat > backend/app/schemas/user.py <<'PY'
from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
PY

# 5. services/auth_service.py
cat > backend/app/services/auth_service.py <<'PY'
import hashlib

# 简单内存用户表
_users = {}

def sha1_hash(password: str) -> str:
    return hashlib.sha1(password.encode()).hexdigest()

def register(username: str, password: str):
    if username in _users:
        return None
    _users[username] = sha1_hash(password)
    return {"username": username}

def login(username: str, password: str):
    hashed = sha1_hash(password)
    if username in _users and _users[username] == hashed:
        return {"username": username}
    return None
PY

# 6. api/v1/auth.py
cat > backend/app/api/v1/auth.py <<'PY'
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
PY

# 7. api/v1/analytics.py
cat > backend/app/api/v1/analytics.py <<'PY'
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/kpis")
def kpis():
    return {
        "collect_yesterday": 12845,
        "partitions": 248,
        "top_app": {"name":"华为应用市场","rating":4.8,"category":"工具"},
        "top_category": {"name":"游戏","share":"32.5%","apps":128},
        "predict_cover": 89.7,
        "task_success": 96.2
    }

@router.get("/topn-trend")
def topn_trend(days:int=7, top:int=5):
    x = ["6/10","6/11","6/12","6/13","6/14","6/15","6/16"]
    return {"x": x, "series": {
        "华为应用市场":[1,1,1,1,1,1,1],
        "微信":[2,2,3,2,2,2,2],
        "抖音":[3,3,2,3,3,3,3],
        "支付宝":[4,4,4,4,5,4,4],
        "淘宝":[5,5,5,5,4,5,5]
    }}

@router.get("/category-share")
def category_share():
    return [
        {"name":"游戏","value":325},{"name":"社交","value":244},{"name":"工具","value":188},
        {"name":"娱乐","value":155},{"name":"教育","value":102},{"name":"其他","value":85}
    ]

@router.get("/region-heatmap")
def region_heatmap():
    return [
        {"name":"北京","value":150},{"name":"天津","value":80},{"name":"上海","value":180},
        {"name":"广东","value":170},{"name":"浙江","value":130},{"name":"江苏","value":120},
        {"name":"四川","value":100},{"name":"福建","value":95},{"name":"山东","value":90}
    ]

@router.get("/task-gantt")
def task_gantt():
    return [
        {"name":"数据采集","start":"2023-06-15 08:00","end":"2023-06-15 09:30","color":"#00B42A"},
        {"name":"数据清洗","start":"2023-06-15 09:30","end":"2023-06-15 10:45","color":"#00B42A"},
        {"name":"数据分析","start":"2023-06-15 10:45","end":"2023-06-15 12:30","color":"#00B42A"},
        {"name":"数据预测","start":"2023-06-15 12:30","end":"2023-06-15 14:15","color":"#FF7D00"},
        {"name":"报表生成","start":"2023-06-15 14:15","end":"2023-06-15 15:00","color":"#165DFF"}
    ]
PY

# 8. __init__.py 让导入生效
touch backend/app/__init__.py backend/app/api/__init__.py backend/app/api/v1/__init__.py backend/app/core/__init__.py backend/app/schemas/__init__.py backend/app/services/__init__.py backend/app/db/__init__.py backend/app/db/models/__init__.py