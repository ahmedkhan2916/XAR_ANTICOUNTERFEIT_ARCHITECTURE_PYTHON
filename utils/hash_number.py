import hashlib

def generate_seed(data):
    return int(hashlib.sha256(data.encode()).hexdigest(), 16) % (10**8)