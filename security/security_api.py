from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os

# -----------------------------
# IMPORT YOUR MODULES
# -----------------------------
from pattern.generator import generate_pattern_matrix
from pattern.signature import apply_signature
from pattern.renderer import draw_pattern

from pattern.fingerprint import generate_fingerprint, fingerprint_hash
from utils.hash_number import generate_seed

from security.signature import SignatureEngine
from scanner.extractor import scan_pattern

app = FastAPI()

SECRET = "AhmedSecretKey"
DATABASE = {}

os.makedirs("generated", exist_ok=True)


# -----------------------------------
# MODELS
# -----------------------------------
class RegisterRequest(BaseModel):
    pid: str
    ctx: str
    bin: str


# -----------------------------------
# 🔥 PATTERN VALIDATION (ANTI-RANDOM)
# -----------------------------------
def validate_pattern_structure(matrix):
    if matrix is None:
        return False

    size = len(matrix)
    total = size * size

    white = sum(row.count("W") for row in matrix)
    green = sum(row.count("G") for row in matrix)

    white_ratio = white / total
    green_ratio = green / total

    # tuned rules
    if white_ratio < 0.1 or white_ratio > 0.7:
        return False

    if green_ratio < 0.2:
        return False

    return True


# -----------------------------------
# 🔥 FINGERPRINT SIMILARITY
# -----------------------------------
def fingerprint_similarity(fp1, fp2):
    match = 0
    total = len(fp1)

    for a, b in zip(fp1, fp2):
        if a == b:
            match += 1

    return match / total


# -----------------------------------
# REGISTER PRODUCT (AUTO IMAGE)
# -----------------------------------
@app.post("/register")
def register_product(data: RegisterRequest):

    seed = generate_seed(data.pid)

    matrix = generate_pattern_matrix(25, seed)
    matrix = apply_signature(matrix)

    # 🔥 generate image
    img = draw_pattern(matrix, cell_size=20, seed=seed)

    image_name = f"{data.pid}.png"
    image_path = os.path.join("generated", image_name)

    img.save(image_path)

    # fingerprint
    fingerprint = generate_fingerprint(matrix)
    fp_hash = fingerprint_hash(fingerprint)

    # signature
    signature_engine = SignatureEngine(SECRET)

    signature = signature_engine.generate_signature(
        data.bin,
        fp_hash,
        data.ctx
    )

    # store
    DATABASE[data.pid] = {
        "fingerprint_hash": fp_hash,
        "fingerprint": fingerprint,   # 🔥 IMPORTANT
        "signature": signature,
        "is_scanned": False,
        "image_path": image_path
    }

    return {
        "status": "registered",
        "fingerprint_hash": fp_hash,
        "signature": signature,
        "image_path": image_path
    }


# -----------------------------------
# GET IMAGE
# -----------------------------------
@app.get("/get-image/{pid}")
def get_image(pid: str):
    record = DATABASE.get(pid)

    if not record:
        return {"error": "Not found"}

    return FileResponse(record["image_path"])


# -----------------------------------
# VERIFY IMAGE (FINAL SYSTEM)
# -----------------------------------
@app.post("/verify-image")
def verify_image(file: UploadFile = File(...)):

    try:
        temp_path = f"temp_{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -------------------------
        # STEP 1: SCAN
        # -------------------------
        matrix = scan_pattern(temp_path)

        if matrix is None:
            return {
                "final_status": "ERROR",
                "error": "Pattern not detected"
            }

        # 🔥 STEP 2: VALIDATE STRUCTURE
        if not validate_pattern_structure(matrix):
            return {
                "final_status": "INVALID_PATTERN"
            }

        # -------------------------
        # STEP 3: FINGERPRINT
        # -------------------------
        fingerprint = generate_fingerprint(matrix)
        fp_hash = fingerprint_hash(fingerprint)

        # -------------------------
        # STEP 4: MATCH DATABASE
        # -------------------------
        for pid, record in DATABASE.items():

            similarity = fingerprint_similarity(
                fingerprint,
                record["fingerprint"]
            )

            # 🔥 threshold tuning
            if similarity > 0.85:

                if not record["is_scanned"]:
                    record["is_scanned"] = True
                    ownership = "first_scan"
                else:
                    ownership = "already_scanned"

                return {
                    "final_status": "GENUINE",
                    "pid": pid,
                    "ownership_status": ownership,
                    "similarity": similarity
                }

        return {
            "final_status": "INVALID_SCAN"
        }

    except Exception as e:
        return {
            "final_status": "ERROR",
            "error": str(e)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)