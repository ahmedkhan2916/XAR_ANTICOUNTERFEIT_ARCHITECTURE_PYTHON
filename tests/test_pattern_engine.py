# tests/test_pattern_engine.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.virtual_color import VirtualColorMapper
from core.pattern_engine import PatternEngine

mapper = VirtualColorMapper("AhmedSecretKey")
pattern_engine = PatternEngine(matrix_size=5)

binary = "01011000110110110111000101110010010111011100110101"  # Example binary data
context = "PID123_TIME456"

# Step 1: Encode

encode_result = mapper.encode(binary, context)

colors = encode_result["colors"]
mapping = encode_result["mapping"]

# Step 2: Generate matrix
matrix = pattern_engine.generate_matrix(colors)

print("\nMatrix:")
pattern_engine.print_matrix(matrix)

# Step 3: Validate
valid, issues = pattern_engine.validate_pattern(matrix)

print("\nValid Pattern:", valid)
print("Issues:", issues)

# Step 4: Hash
pattern_hash = pattern_engine.generate_pattern_hash(matrix)

print("\nPattern Hash:", pattern_hash)