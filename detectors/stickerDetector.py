import cv2
import numpy as np
import sys
from pathlib import Path


# =========================================================
# PATH HELPERS
# =========================================================

def resolve_input_path(image_path):
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
        project_root / "generated" / input_path,
        project_root / "detectors" / input_path,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


def resolve_output_path(output_path):
    resolved_path = Path(output_path).expanduser()

    if not resolved_path.is_absolute():
        resolved_path = Path.cwd() / resolved_path

    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    return resolved_path


# =========================================================
# HEIC SUPPORT
# =========================================================

def is_heic_file(image_path):
    with open(image_path, "rb") as file:
        header = file.read(32)

    return (
        b"ftypheic" in header
        or b"ftypheix" in header
        or b"ftyphevc" in header
    )


def load_image(image_path):
    image = cv2.imread(str(image_path))

    if image is not None:
        return image

    if not is_heic_file(image_path):
        return None

    try:
        import pillow_heif
        from PIL import Image
    except ImportError as error:
        raise ValueError(
            f"{image_path} is HEIC/HEIF image. "
            "Install pillow-heif or convert image."
        ) from error

    pillow_heif.register_heif_opener()

    with Image.open(image_path) as heic_image:
        rgb_image = heic_image.convert("RGB")
        return cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)


# =========================================================
# ORDER POINTS
# =========================================================

def  order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)

    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


# =========================================================
# PERSPECTIVE TRANSFORM
# =========================================================

def four_point_transform(image, pts):
    rect = order_points(pts)

    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)

    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    maxHeight = max(int(heightA), int(heightB))

    if maxWidth <= 0 or maxHeight <= 0:
        raise ValueError("Invalid crop dimensions")

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, dst)

    warped = cv2.warpPerspective(
        image,
        matrix,
        (maxWidth, maxHeight)
    )

    return warped


# =========================================================
# DEBUG DRAW
# =========================================================

def draw_detected_corners(image, points, output_path):
    debug_image = image.copy()

    ordered = order_points(points.reshape(4, 2)).astype(int)

    cv2.polylines(
        debug_image,
        [ordered],
        True,
        (0, 255, 0),
        6
    )

    for index, point in enumerate(ordered):
        x, y = point

        cv2.circle(
            debug_image,
            (x, y),
            16,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            debug_image,
            str(index + 1),
            (x + 20, y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 0, 0),
            3
        )

    cv2.imwrite(str(output_path), debug_image)


def remove_header_band(warped):

    gray = cv2.cvtColor(
        warped,
        cv2.COLOR_BGR2GRAY
    )

    height, width = gray.shape[:2]
    dark_pixels = gray < 100
    row_density = dark_pixels.sum(axis=1).astype(float)

    smooth = np.convolve(
        row_density,
        np.ones(15) / 15,
        mode="same"
    )

    high_density = max(50, width * 0.12)
    low_density = width * 0.07

    min_y = int(height * 0.08)
    max_y = int(height * 0.35)

    if smooth[:min_y].mean() >= low_density:
        return warped

    for y in range(min_y, max_y):
        previous_band = smooth[
            max(0, y - 35):max(0, y - 10)
        ]

        next_band = smooth[
            y:min(height, y + 25)
        ]

        if (
            len(previous_band) > 0
            and len(next_band) > 0
            and previous_band.mean() < low_density
            and next_band.mean() > high_density
        ):
            return warped[y:, :]

    return warped


# =========================================================
# STICKER DETECTOR
# =========================================================

def find_big_sticker_contour(binary, image_shape):

    height, width = image_shape[:2]

    image_area = height * width

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (9, 9)
    )

    # =====================================================
    # CONNECT GRID STRUCTURES
    # =====================================================

    morph = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    morph = cv2.dilate(
        morph,
        kernel,
        iterations=1
    )

    contours, _ = cv2.findContours(
        morph,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    best_contour = None
    best_score = -999

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < image_area * 0.05:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        aspect_ratio = w / float(h)

        # =================================================
        # STICKER SHOULD BE NEAR SQUARE
        # =================================================

        if aspect_ratio < 0.7 or aspect_ratio > 1.3:
            continue

        extent = area / float(w * h)

        # =================================================
        # REMOVE WEIRD SHAPES
        # =================================================

        if extent < 0.45:
            continue

        perimeter = cv2.arcLength(contour, True)

        approx = cv2.approxPolyDP(
            contour,
            0.03 * perimeter,
            True
        )

        if len(approx) == 4:
            candidate = approx

        else:
            rect = cv2.minAreaRect(contour)

            candidate = cv2.boxPoints(rect)

            candidate = candidate.reshape(4, 1, 2)

        candidate_area = cv2.contourArea(candidate)

        rectangularity = candidate_area / max(w * h, 1)

        score = (
            rectangularity * 4
            + extent * 3
            + (area / image_area)
        )

        if score > best_score:
            best_score = score
            best_contour = candidate.astype("float32")

    return best_contour


# =========================================================
# MAIN DETECTOR
# =========================================================

def  detect_sticker(
    image_path,
    output_path,
    debug_output_path=None
):

    resolved_input = resolve_input_path(image_path)

    if resolved_input is None:
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = load_image(resolved_input)

    if image is None:
        raise ValueError(
            f"Could not read image: {resolved_input}"
        )

    original = image.copy()

    # =====================================================
    # RESIZE
    # =====================================================

    target_width = 1200

    scale = target_width / image.shape[1]

    image = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale
    )

    ratio = original.shape[1] / image.shape[1]

    # =====================================================
    # PREPROCESS
    # =====================================================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blur = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    # =====================================================
    # STRUCTURE DETECTION
    # =====================================================

    adaptive = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        5
    )

    # =====================================================
    # FIND STICKER
    # =====================================================

    screen_contour = find_big_sticker_contour(
        adaptive,
        image.shape
    )

    if screen_contour is None:
        raise ValueError(
            "Sticker not detected"
        )

    pts = screen_contour.reshape(4, 2) * ratio

    # =====================================================
    # DEBUG OUTPUT
    # =====================================================

    if debug_output_path is not None:

        draw_detected_corners(
            original,
            pts.reshape(4, 1, 2),
            resolve_output_path(debug_output_path)
        )

    # =====================================================
    # PERSPECTIVE CORRECTION
    # =====================================================

    warped = four_point_transform(
        original,
        pts
    )

    # =====================================================
    # SAFE FINAL CROP
    # =====================================================

    h, w = warped.shape[:2]

    safe_margin_x = int(w * 0.01)
    safe_margin_y = int(h * 0.01)

    warped = warped[
        safe_margin_y:h - safe_margin_y,
        safe_margin_x:w - safe_margin_x
    ]

    warped = remove_header_band(warped)

    # =====================================================
    # FINAL NORMALIZATION
    # =====================================================

    warped = cv2.resize(
        warped,
        (800, 800)
    )

    # =====================================================
    # SAVE
    # =====================================================

    resolved_output = resolve_output_path(output_path)

    saved = cv2.imwrite(
        str(resolved_output),
        warped
    )

    if not saved:
        raise ValueError(
            f"Could not save output image: {resolved_output}"
        )

    return warped


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "\nUsage:\n"
            "python stickerDetector.py input.jpg output.png [debug.png]\n"
        )

        sys.exit()

    input_path = sys.argv[1]

    output_path = sys.argv[2]

    debug_output_path = (
        sys.argv[3]
        if len(sys.argv) >= 4
        else None
    )

    try:

        detect_sticker(
            input_path,
            output_path,
            debug_output_path
        )

        print("\nSticker normalized successfully\n")

    except Exception as error:

        print(f"\nError: {error}\n")

        sys.exit(1)
