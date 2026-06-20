from PIL import Image
import numpy as np

# -----------------------------------
# COLOR MAP
# -----------------------------------
COLOR_MAP = {
    "G": np.array([46, 204, 113]),
    "B": np.array([52, 152, 219]),
    "Y": np.array([241, 196, 15]),
    "R": np.array([231, 76, 60]),
    "K": np.array([0, 0, 0]),
    "W": np.array([255, 255, 255])
}


# -----------------------------------
# FIND CLOSEST COLOR
# -----------------------------------
def closest_color(pixel):
    best = "W"
    min_dist = float("inf")

    for k, v in COLOR_MAP.items():
        d = np.linalg.norm(pixel - v)
        if d < min_dist:
            min_dist = d
            best = k

    return best


# -----------------------------------
# SMART CROP (WITH PADDING)
# -----------------------------------
def crop_pattern_area(img):
    gray = np.mean(img, axis=2)

    mask = gray < 250
    coords = np.argwhere(mask)

    if len(coords) == 0:
        return None

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    # 🔥 FIX: add padding (VERY IMPORTANT)
    padding = 5

    y0 = max(0, y0 - padding)
    x0 = max(0, x0 - padding)
    y1 = min(img.shape[0], y1 + padding)
    x1 = min(img.shape[1], x1 + padding)

    return img[y0:y1, x0:x1]


# -----------------------------------
# SAMPLE REGION (NOT SINGLE PIXEL)
# -----------------------------------
def sample_cell(img, x, y, cell_w, cell_h):
    x1 = int(x - cell_w * 0.2)
    x2 = int(x + cell_w * 0.2)
    y1 = int(y - cell_h * 0.2)
    y2 = int(y + cell_h * 0.2)

    h, w, _ = img.shape

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w - 1, x2)
    y2 = min(h - 1, y2)

    region = img[y1:y2, x1:x2]

    if region.size == 0:
        return "W"

    avg_color = np.mean(region.reshape(-1, 3), axis=0)

    return closest_color(avg_color)


# -----------------------------------
# MAIN SCAN FUNCTION
# -----------------------------------
def scan_pattern(image_path, grid_size=25):

    img = Image.open(image_path).convert("RGB")
    img = np.array(img)

    # crop first
    img = crop_pattern_area(img)
    if img is None:
        return None

    h, w, _ = img.shape

    cell_h = h / grid_size
    cell_w = w / grid_size

    matrix = []

    for i in range(grid_size):
        row = []
        for j in range(grid_size):

            y = (i + 0.5) * cell_h
            x = (j + 0.5) * cell_w

            color = sample_cell(img, x, y, cell_w, cell_h)

            row.append(color)

        matrix.append(row)

    return matrix