import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from core.virtual_color import VirtualColorMapper
from core.pattern_engine import PatternEngine
from security.signature import SignatureEngine


class PayloadBuilder:
    def __init__(self, secret):
        self.mapper = VirtualColorMapper(secret)
        self.pattern_engine = PatternEngine()
        self.signature_engine = SignatureEngine(secret)

    def create_payload(self, product_id, binary_data, context):
        # Encode
        encode_result = self.mapper.encode(binary_data, context)
        colors = encode_result["colors"]

        # Pattern
        matrix = self.pattern_engine.generate_matrix(colors)
        pattern_hash = self.pattern_engine.generate_pattern_hash(matrix)

        # Signature
        signature = self.signature_engine.generate_signature(
            binary_data,
            pattern_hash,
            context
        )

        payload = {
            "pid": product_id,
            "ctx": context,
            "bin": binary_data,
            "sig": signature
        }

        return json.dumps(payload)