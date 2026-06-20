import json
import sys
from pathlib import Path

import numpy as np


def resolve_map_path(map_path):
    input_path = Path(map_path).expanduser()

    if input_path.is_absolute():
        return input_path if input_path.is_file() else None

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    candidates = [
        Path.cwd() / input_path,
        script_dir / input_path,
        project_root / input_path,
        project_root / "forensics" / input_path,
        project_root / "preprocessing" / input_path,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


def load_map(path):
    resolved_path = resolve_map_path(path)

    if resolved_path is None:
        raise FileNotFoundError(f"Map file not found: {path}")

    if resolved_path.stat().st_size == 0:
        raise ValueError(f"Map file is empty: {resolved_path}")

    encodings = ["utf-8", "utf-8-sig", "utf-16"]

    for encoding in encodings:
        try:
            with open(resolved_path, "r", encoding=encoding) as file:
                return json.load(file)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON in {resolved_path}: {error}") from error

    raise ValueError(f"Could not read map file encoding: {resolved_path}")


def calculate_region_difference(region1, region2):
    keys = [
        "edgeTurbulence",
        "localVariance",
        "bleedScore",
        "edgeDensity",
    ]

    differences = []

    for key in keys:
        if key not in region1 or key not in region2:
            continue

        differences.append(abs(region1[key] - region2[key]))

    if len(differences) == 0:
        return None

    return float(np.mean(differences))


def compare_maps(original_map, scanned_map):
    region_differences = []
    suspicious_regions = []
    total_regions = 0

    for region_key in original_map:
        if region_key not in scanned_map:
            continue

        diff = calculate_region_difference(
            original_map[region_key],
            scanned_map[region_key],
        )

        if diff is None:
            continue

        region_differences.append(diff)
        total_regions += 1

        if diff > 8:
            suspicious_regions.append(region_key)

    if total_regions == 0:
        return {
            "error": "No matching regions found",
            "totalRegions": 0,
        }

    average_difference = float(np.mean(region_differences))
    suspicious_ratio = len(suspicious_regions) / total_regions

    if average_difference < 3 and suspicious_ratio < 0.10:
        verdict = "GENUINE"
    elif average_difference < 7 and suspicious_ratio < 0.30:
        verdict = "SUSPICIOUS"
    else:
        verdict = "FAKE"

    return {
        "verdict": verdict,
        "averageDifference": round(average_difference, 3),
        "suspiciousRatio": round(float(suspicious_ratio), 3),
        "suspiciousRegions": suspicious_regions[:20],
        "totalRegions": total_regions,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Provide original and scanned maps",
            "hint": "Example: python compareForensicsRegions.py originalMap.json geminiMap.json",
        }, indent=4))
        sys.exit()

    original_path = sys.argv[1]
    scanned_path = sys.argv[2]

    try:
        original_map = load_map(original_path)
        scanned_map = load_map(scanned_path)
    except (FileNotFoundError, ValueError) as error:
        print(json.dumps({
            "error": str(error),
            "hint": "Create map JSON with: python localForensicsRegions.py image.jpg > map.json",
        }, indent=4))
        sys.exit()

    result = compare_maps(original_map, scanned_map)

    print(json.dumps(result, indent=4))
