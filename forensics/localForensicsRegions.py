import cv2
import numpy as np
import json
import sys
from pathlib import Path


def resolve_image_path(image_path):
    input_path = Path(image_path).expanduser()

    if input_path.is_absolute():
        return input_path if input_path.is_file() else None

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    candidates = [
        Path.cwd() / input_path,
        script_dir / input_path,
        project_root / input_path,
        project_root / "preprocessing" / input_path,
        project_root / "forensics" / input_path,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


# ====================================
# ANALYZE SINGLE REGION
# ====================================

def analyze_region(region):

    # EDGE MAP
    edges = cv2.Canny(region, 80, 160)

    edge_turbulence = np.std(edges)

    # LOCAL VARIANCE
    local_mean = cv2.blur(region, (5, 5))
    local_variance = np.mean((region - local_mean) ** 2)

    # BLEED SCORE
    laplacian = cv2.Laplacian(region, cv2.CV_64F)
    bleed_score = np.mean(np.abs(laplacian))

    # EDGE DENSITY
    edge_density = np.sum(edges > 0) / edges.size

    return {
        "edgeTurbulence": round(float(edge_turbulence), 3),
        "localVariance": round(float(local_variance), 3),
        "bleedScore": round(float(bleed_score), 3),
        "edgeDensity": round(float(edge_density), 5)
    }


# ====================================
# MAIN REGION ENGINE
# ====================================

def build_local_forensic_map(image_path):

    resolved_path = resolve_image_path(image_path)

    if resolved_path is None:
        return {
            "error": "Image not found",
            "requestedPath": image_path
        }

    image = cv2.imread(str(resolved_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return {
            "error": "Image could not be read",
            "resolvedPath": str(resolved_path)
        }

    # LIGHT BLUR
    image = cv2.GaussianBlur(image, (3, 3), 0)

    height, width = image.shape

    # ====================================
    # GRID SIZE
    # ====================================

    rows = 20
    cols = 20

    block_h = height // rows
    block_w = width // cols

    forensic_map = {"ForensicData":{}}

    region_id = 0

    # ====================================
    # LOOP REGIONS
    # ====================================

    for y in range(rows):

        for x in range(cols):

            start_y = y * block_h
            end_y = start_y + block_h

            start_x = x * block_w
            end_x = start_x + block_w

            region = image[
                start_y:end_y,
                start_x:end_x
            ]

            region_metrics = analyze_region(region)

            forensic_map["ForensicData"][f"region_{region_id}"] = region_metrics

            region_id += 1

       
           

    return forensic_map


# ====================================
# TERMINAL EXECUTION
# ====================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(json.dumps({
            "error": "Provide image path"
        }))

        sys.exit()

    image_path = sys.argv[1]

    result = build_local_forensic_map(image_path)

    print(json.dumps(result, indent=4))
