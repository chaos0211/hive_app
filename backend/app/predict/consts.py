# backend/app/predict/consts.py
BRAND_KEY_MAP = {"free": "rank_a", "paid": "rank_b", "grossing": "rank_c"}

def brand_key(brand: str) -> str:
    k = BRAND_KEY_MAP.get((brand or "").lower())
    if not k:
        raise ValueError("brand must be one of: free, paid, grossing")
    return k