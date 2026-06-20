import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from core.virtual_color import VirtualColorMapper
from core.pattern_engine import PatternEngine
from security.signature import SignatureEngine
from core.verifier import Verifier

secret = "AhmedSecretKey"
context = "PID123_TIME456"
binary = "01011000110110110111000101110010010111011100110101"

# Step 1: Generate valid system data
mapper = VirtualColorMapper(secret)
pattern_engine = PatternEngine()
signature_engine = SignatureEngine(secret)

encode_result = mapper.encode(binary, context)
colors = encode_result["colors"]

matrix = pattern_engine.generate_matrix(colors)
pattern_hash = pattern_engine.generate_pattern_hash(matrix)

signature = signature_engine.generate_signature(binary, pattern_hash, context)

# Step 2: Verify
verifier = Verifier(secret)

result = verifier.verify(binary, context, signature)

print("\nVerification Result:")
for k, v in result.items():
    print(f"{k}: {v}")