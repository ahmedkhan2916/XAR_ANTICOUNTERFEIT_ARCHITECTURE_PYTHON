import hashlib

def generate_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()