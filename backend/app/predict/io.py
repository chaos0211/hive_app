# backend/app/predict/io.py
import os, torch
from typing import Dict, Any

MODEL_DIR = os.environ.get("PREDICT_MODEL_DIR", "backend/models/lstm")

def model_path(app_id: str, country: str, device: str, brand: str) -> str:
    os.makedirs(MODEL_DIR, exist_ok=True)
    name = f"{country}_{device}_{brand}_{app_id}.pt"
    return os.path.join(MODEL_DIR, name)

def save_model(path: str, state: Dict[str, Any]):
    torch.save(state, path)

def load_model(path: str) -> Dict[str, Any]:
    return torch.load(path, map_location="cpu")