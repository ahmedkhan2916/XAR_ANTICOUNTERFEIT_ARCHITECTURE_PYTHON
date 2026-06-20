import hashlib
import json


COLOR_MAP = {
    "#2ecc71": "G",
    "#3498db": "B",
    "#f1c40f": "Y",
    "#e74c3c": "R",
    "#000000": "K"
}


def get_zone(i, j, size):
    margin_outer = int(size * 0.1)
    margin_inner = int(size * 0.2)

    if i < margin_outer or j < margin_outer or i >= size - margin_outer or j >= size - margin_outer:
        return "outer"

    elif i > margin_inner and j > margin_inner and i < size - margin_inner and j < size - margin_inner:
        return "inner"

    else:
        return "mid"


def generate_fingerprint(matrix):
    size = len(matrix)

    color_count = {"G":0,"B":0,"Y":0,"R":0,"K":0}
    zones = {
        "outer": {"G":0,"B":0,"Y":0,"R":0,"K":0},
        "mid":   {"G":0,"B":0,"Y":0,"R":0,"K":0},
        "inner": {"G":0,"B":0,"Y":0,"R":0,"K":0}
    }

    transitions = 0

    for i in range(size):
        for j in range(size):
            color = matrix[i][j]

            # ❗ skip white background
            if color == "#ffffff":
                continue

            mapped = COLOR_MAP.get(color)
            if not mapped:
                continue

            # color count
            color_count[mapped] += 1

            # zone count
            zone = get_zone(i, j, size)
            zones[zone][mapped] += 1

            # transitions
            if j > 0 and matrix[i][j] != matrix[i][j-1]:
                transitions += 1

    fingerprint = {
        "color_distribution": color_count,
        "zones": zones,
        "transitions": transitions
    }

    return fingerprint


def fingerprint_hash(fingerprint):
    data = json.dumps(fingerprint, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()