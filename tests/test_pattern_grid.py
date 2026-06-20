import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# from core.pattern_grid import hash_to_pattern
# from utils.grid_drawer import draw_pattern_v3_2

# product_id = "P123"
# context = "PID123_TIME456"
# secret = "AhmedSecretKey"

# matrix, hash_value = hash_to_pattern(product_id, context, secret)

# draw_pattern_v3_2(matrix, hash_value)



# from pattern.generator import generate_pattern_matrix
# from pattern.signature import apply_signature
# from pattern.renderer import draw_pattern
# from utils.hash_number import generate_seed

# import random
# from datetime import datetime

# # -------------------------
# # CONFIG
# # -------------------------
# data = "PRODUCT123"
# size = 25
# cell_size = 20

# # -------------------------
# # SEED CONTROL (IMPORTANT)
# # -------------------------
# seed = generate_seed(data)
# random.seed(seed)  # ensures reproducible pattern

# # -------------------------
# # GENERATE MATRIX
# # -------------------------
# matrix = generate_pattern_matrix(size, seed)
# matrix = apply_signature(matrix)

# # -------------------------
# # RENDER IMAGE
# # -------------------------
# img = draw_pattern(matrix, seed=seed)

# # -------------------------
# # SAVE WITH VERSION + TIME
# # -------------------------
# timestamp = datetime.now().strftime("%H%M%S")
# filename = f"pattern_v4_8_{timestamp}.png"

# img.save(filename)

# print(f"Pattern generated: {filename}")




from pattern.generator import generate_pattern_matrix
from pattern.signature import apply_signature
from pattern.renderer import draw_pattern
from pattern.fingerprint import generate_fingerprint
from utils.hash_number import generate_seed

data = "PRODUCT123"

seed = generate_seed(data)

matrix = generate_pattern_matrix(25, seed)
matrix = apply_signature(matrix)

# IMPORTANT: pass seed to renderer (determinism)
img = draw_pattern(matrix, seed=seed)
img.save("pattern_v4_88.png")

fp= generate_fingerprint(matrix)

print("Fingerprint:", fp)