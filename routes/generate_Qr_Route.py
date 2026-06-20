from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
import qrcode
import cv2
from pathlib import Path
from preprocessing.normalizeLightining import normalize_lighting
from preprocessing.simulatePrintPhysics import simulate_print_physics
app = FastAPI()


class QRRequest(BaseModel):
    product_id: str
    signature: str
    pattern_hash: str
    verificationToken: str
    pattern_image_path: str
    output_path: str
   

@app.post("/generate-qr")
def generate_qr(req: QRRequest):
    qr_data = f"XAR|PID:{req.product_id}|SIG:{req.signature}|PH:{req.verificationToken}"
    
   
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,  # quiet zone inside QR
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    pattern = Image.open(req.pattern_image_path).convert("RGB")

    # MATCH GRID STRUCTURE EXACTLY
    GRID_SIZE = 20
    QR_ZONE_CELLS = 6

    cell_size = pattern.width // GRID_SIZE
    qr_size = cell_size * QR_ZONE_CELLS

    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)

    # center placement
    center_x = pattern.width // 2
    center_y = pattern.height // 2

    x = center_x - qr_size // 2
    y = center_y - qr_size // 2

    pattern.paste(qr_img, (x, y))

    output_path = Path(req.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pattern.save(output_path)

    #simulatePrintPhysics Pipeline

    simulate_output_path = output_path.with_name(f"{output_path.stem}_simulate{output_path.suffix}")
    sticker_image = cv2.imread(str(output_path))
    if sticker_image is None:
        raise Exception("Generated sticker image not found")

    simulated = simulate_print_physics(sticker_image)
    cv2.imwrite(str(simulate_output_path), simulated)
 



    #send qr sticker to normalize before sending to nodejs

    normalized_output_path = output_path.with_name(f"{output_path.stem}_final_normalized{output_path.suffix}")
    normalize_lighting(str(simulate_output_path), str(normalized_output_path))

    return {
        "status": "success",
        "final_output": str(normalized_output_path),
        "output": str(output_path),
        "simulated_output": str(simulate_output_path),
        "normalized_output": str(normalized_output_path),
    }
