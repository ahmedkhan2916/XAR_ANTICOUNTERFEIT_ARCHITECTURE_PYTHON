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


def analyze_physical_print(image_path):

    # =========================
    # LOAD IMAGE
    # =========================
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

    # =========================
    # BLUR REDUCTION
    # =========================
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # =========================
    # EDGE DETECTION
    # =========================
    edges = cv2.Canny(image, 80, 160)

    # =========================
    # EDGE TURBULENCE
    # =========================
    edge_std = np.std(edges)

    # =========================
    # LOCAL CONTRAST
    # =========================
    local_mean = cv2.blur(image, (9, 9))
    local_variance = np.mean((image - local_mean) ** 2)

    # =========================
    # LINE CONTINUITY
    # =========================
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=40,
        minLineLength=20,
        maxLineGap=5
    )

    line_lengths = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            length = np.sqrt(
                (x2 - x1) ** 2 +
                (y2 - y1) ** 2
            )

            line_lengths.append(length)

    average_line_length = (
        np.mean(line_lengths)
        if len(line_lengths) > 0
        else 0
    )

    # =========================
    # DOT PHYSICS
    # =========================
    _, thresh = cv2.threshold(
        image,
        120,
        255,
        cv2.THRESH_BINARY_INV
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    circularities = []

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area < 5 or area > 200:
            continue

        perimeter = cv2.arcLength(cnt, True)

        if perimeter == 0:
            continue

        circularity = (
            4 * np.pi * area
        ) / (perimeter * perimeter)

        circularities.append(circularity)

    average_circularity = (
        np.mean(circularities)
        if len(circularities) > 0
        else 0
    )

    # =========================
    # BLEED ANALYSIS
    # =========================
    laplacian = cv2.Laplacian(
        image,
        cv2.CV_64F
    )

    bleed_score = np.mean(np.abs(laplacian))

    # =========================
    # FINAL RESULT
    # =========================
    result = {"PhysicalPrintData":{
        "edgeTurbulence": round(float(edge_std), 3),
        "localVariance": round(float(local_variance), 3),
        "lineContinuity": round(float(average_line_length), 3),
        "dotCircularity": round(float(average_circularity), 3),
        "bleedScore": round(float(bleed_score), 3)}
    }

    return result


# =========================
# TERMINAL EXECUTION
# =========================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Provide image path"
        }))
        sys.exit()

    image_path = sys.argv[1]

    result = analyze_physical_print(image_path)

    print(json.dumps(result, indent=4))
