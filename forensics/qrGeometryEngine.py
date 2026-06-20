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

# ============================================
# LOAD IMAGE
# ============================================

def load_image(image_path):

    resolved_path = resolve_image_path(image_path)

    if resolved_path is None:
        return None, None

    image = cv2.imread(str(resolved_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return None, resolved_path

    return image, resolved_path


# ============================================
# EXTRACT QR REGION
# ============================================

def extract_qr_region(image):

    detector = cv2.QRCodeDetector()
    variants = [
        image,
        cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1],
        cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            5
        )
    ]

    for variant in variants:
        for scale in (1, 2):
            scan_image = (
                cv2.resize(
                    variant,
                    None,
                    fx=scale,
                    fy=scale,
                    interpolation=cv2.INTER_CUBIC
                )
                if scale > 1
                else variant
            )

            detected, points = detector.detect(scan_image)

            if not detected or points is None:
                continue

            points = np.asarray(points, dtype=np.float32).reshape(-1, 2)

            if len(points) < 4:
                continue

            height, width = scan_image.shape[:2]

            x_min = max(0, int(np.floor(np.min(points[:, 0]))))
            y_min = max(0, int(np.floor(np.min(points[:, 1]))))

            x_max = min(width, int(np.ceil(np.max(points[:, 0]))))
            y_max = min(height, int(np.ceil(np.max(points[:, 1]))))

            if x_max <= x_min or y_max <= y_min:
                continue

            qr = scan_image[y_min:y_max, x_min:x_max]

            if qr.ndim == 2 and qr.size > 0:
                return qr

    return None


# ============================================
# MODULE UNIFORMITY
# ============================================

def calculate_module_uniformity(binary):

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    widths = []
    heights = []

    for c in contours:

        x, y, w, h = cv2.boundingRect(c)

        if w > 3 and h > 3:
            widths.append(w)
            heights.append(h)

    if len(widths) == 0:
        return 0

    width_std = np.std(widths)
    height_std = np.std(heights)

    uniformity = 1 / (1 + width_std + height_std)

    return round(float(uniformity), 3)


# ============================================
# EDGE TURBULENCE
# ============================================

def calculate_edge_turbulence(binary):

    edges = cv2.Canny(binary, 100, 200)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE
    )

    turbulence_scores = []

    for c in contours:

        if len(c) < 10:
            continue

        perimeter = cv2.arcLength(c, True)

        approx = cv2.approxPolyDP(
            c,
            0.01 * perimeter,
            True
        )

        turbulence = abs(len(c) - len(approx))

        turbulence_scores.append(turbulence)

    if len(turbulence_scores) == 0:
        return 0

    return round(float(np.mean(turbulence_scores)), 3)


# ============================================
# SPACING VARIANCE
# ============================================

def calculate_spacing_variance(binary):

    if binary.ndim != 2 or binary.size == 0:
        return 0

    projection = np.sum(binary == 0, axis=0)

    distances = []

    active = False
    start = 0

    for i, val in enumerate(projection):

        if val > 5 and not active:
            start = i
            active = True

        elif val <= 5 and active:
            distances.append(i - start)
            active = False

    if len(distances) == 0:
        return 0

    return round(float(np.var(distances)), 3)


# ============================================
# CORNER SHARPNESS
# ============================================

def calculate_corner_sharpness(binary):

    corners = cv2.goodFeaturesToTrack(
        binary,
        200,
        0.01,
        10
    )

    if corners is None:
        return 0

    return round(float(len(corners)), 3)


# ============================================
# SYNTHETIC RISK SCORE
# ============================================

def calculate_synthetic_risk(
    module_uniformity,
    edge_turbulence,
    spacing_variance,
    corner_sharpness
):

    risk = 0

    # AI tends to have TOO MUCH uniformity
    if module_uniformity > 0.85:
        risk += 30

    # AI tends to have LOW turbulence
    if edge_turbulence < 15:
        risk += 25

    # AI tends to have LOW spacing variance
    if spacing_variance < 10:
        risk += 20

    # AI tends to have TOO MANY sharp corners
    if corner_sharpness > 120:
        risk += 25

    return risk


# ============================================
# MAIN ANALYZER
# ============================================

def analyze_qr_geometry(image_path):

    image, resolved_path = load_image(image_path)

    if image is None:
        if resolved_path is None:
            return {
                "error": "Image not found",
                "requestedPath": image_path
            }

        return {
            "error": "Image could not be read",
            "resolvedPath": str(resolved_path)
        }

    qr = extract_qr_region(image)

    if qr is None:
        return {
            "error": "QR not detected"
        }

    _, binary = cv2.threshold(
        qr,
        127,
        255,
        cv2.THRESH_BINARY
    )

    module_uniformity = calculate_module_uniformity(binary)

    edge_turbulence = calculate_edge_turbulence(binary)

    spacing_variance = calculate_spacing_variance(binary)

    corner_sharpness = calculate_corner_sharpness(binary)

    synthetic_risk = calculate_synthetic_risk(
        module_uniformity,
        edge_turbulence,
        spacing_variance,
        corner_sharpness
    )

    verdict = "GENUINE"

    if synthetic_risk >= 60:
        verdict = "FAKE"

    elif synthetic_risk >= 30:
        verdict = "SUSPICIOUS"

    return { "QRGeometryData":{

        # "verdict": verdict,

        "moduleUniformity": module_uniformity,

        "edgeTurbulence": edge_turbulence,

        "spacingVariance": spacing_variance,

        "cornerSharpness": corner_sharpness,

        "syntheticRisk": synthetic_risk
    }
    }


# ============================================
# TERMINAL EXECUTION
# ============================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(json.dumps({
            "error": "Please provide image path"
        }, indent=4))

        sys.exit()

    image_path = sys.argv[1]

    result = analyze_qr_geometry(image_path)

    print(json.dumps(result, indent=4))
