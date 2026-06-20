import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))



from security.signature import SignatureEngine

engine = SignatureEngine("AhmedSecretKey")

binary = "01011000110110110111000101110010010111011100110101"
pattern_hash = "abc123xyz456"
context = "PID123_TIME456"

# Generate
signature = engine.generate_signature(binary, pattern_hash, context)

print("Signature:", signature)

# Verify
is_valid = engine.verify_signature(binary, pattern_hash, context, signature)

print("Valid:", is_valid)