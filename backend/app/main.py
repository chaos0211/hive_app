from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, analytics,rankings

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
app.include_router(rankings.router)

@app.get("/health")
def health():
    return {"status": "ok"}
