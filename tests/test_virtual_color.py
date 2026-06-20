# test_virtual_color.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# from core.virtual_color import VirtualColorMapper

# mapper = VirtualColorMapper("AhmedSecretKey")

# binary = "001"  # Example binary data
# context = "PID123_TIME456"

# colors, mapping = mapper.encode(binary, context)

# print("Binary:", binary)
# print("Colors:", colors)
# print("Mapping:", mapping)

# decoded = mapper.decode(colors, mapping)
# print("Decoded:", decoded)


from core.virtual_color import VirtualColorMapper

mapper = VirtualColorMapper("AhmedSecretKey")

binary = "01011000110110110111000101110010010111011100110101"   # odd length test
context = "PID123_TIME456"

# Encode
result = mapper.encode(binary, context)

colors = result["colors"]
mapping = result["mapping"]
# original_length = result["original_length"]

print("Original Binary:", binary)
print("Colors:", colors)
print("Mapping:", mapping)
# print("Stored Length:", original_length)

# Decode
decoded = mapper.decode(colors, mapping,original_length=len(binary))

print("Decoded:", decoded)
