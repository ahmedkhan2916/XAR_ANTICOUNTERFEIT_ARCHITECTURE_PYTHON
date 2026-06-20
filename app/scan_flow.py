import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from core.verifier import Verifier
from app.db import get_product, update_product


class ScanFlow:
    def __init__(self, secret):
        self.verifier = Verifier(secret)

    def scan(self, qr_data, user=None, action="scan"):
        data = json.loads(qr_data)

        pid = data["pid"]
        ctx = data["ctx"]
        sig = data["sig"]
        binary = data["bin"]

        product = get_product(pid)

        if not product:
            return "Product not found"

        result = self.verifier.verify(binary, ctx, sig)
        if not result["final_result"]:
            return "Invalid QR"

        if action == "delivery":
            update_product(pid, {"status": "DELIVERED"})
            return "Delivered"

        if action == "customer":
            if product["status"] != "DELIVERED":
                return "Not ready for activation"

            update_product(pid, {"status": "ACTIVATED", "owner": user})
            return "Ownership locked"

        if action == "return":
            if product["status"] != "ACTIVATED":
                return "Return rejected"

            if product["owner"] != user:
                return "Wrong user"

            update_product(pid, {"status": "RETURNED"})
            return "Return accepted"

        return "Scan OK"
