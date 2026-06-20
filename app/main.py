import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from app.payload import PayloadBuilder
from app.db import create_product
from qr.qr_generator import QRGenerator
from app.qr_scanner import QRScanner
from app.scan_flow import ScanFlow

secret = "AhmedSecretKey3"

builder = PayloadBuilder(secret)
qr_gen = QRGenerator()
scanner = ScanFlow(secret)
scanner_device = QRScanner()

scanned_data = scanner_device.scan_from_image("qr.png")

print("\n📱 Scanned Data:")
print(scanned_data)


# Step 1: Create product
binary = "0101100011011011011100010111001001011101110011010101"
context = "PID123_TIME45678"
product_id = "AHMEDENGINEERING_PRODUCT_003"

payload = builder.create_payload(product_id, binary, context)
signature = json.loads(payload)["sig"]

# Store in DB
create_product(product_id, signature)

qr_gen.generate_qr(payload)

print("QR Payload:", payload)

# Step 2: Delivery scan
print(scanner.scan(payload, action="delivery"))

# Step 3: Customer scan
print(scanner.scan(payload, user="user_1", action="customer"))

# Step 4: Return scan
print(scanner.scan(payload, user="user_1", action="return"))

# Step 5: Fraud attempt (second return)
print(scanner.scan(payload, user="user_1", action="return"))
