import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.hash_number import generate_hash

COLORS = ['R', 'G', 'B', 'Y']

def hash_to_pattern(product_id, context, secret, size=25):
    data = f"{product_id}-{context}-{secret}"
    hash_value = generate_hash(data)

    nums = [int(c, 16) for c in hash_value]

    matrix = []
    idx = 0

    for i in range(size):
        row = []
        for j in range(size):
            val = nums[idx % len(nums)]
            color = COLORS[val % 4]   # 🔥 pure hash-based
            row.append(color)
            idx += 1
        matrix.append(row)

    return matrix, hash_value