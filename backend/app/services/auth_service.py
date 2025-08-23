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
