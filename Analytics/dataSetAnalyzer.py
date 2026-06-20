import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, pstdev


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FOLDER_PATH = PROJECT_ROOT / "Datasets" / "GenuineDaylightA12"
OUTPUT_PATH = FOLDER_PATH / "GenuineDaylightA12_OutputResult.json"


def collect_numeric_fields(value, fields):
    """Collect numeric leaf values by field name from nested dictionaries."""
    if not isinstance(value, dict):
        return

    for key, item in value.items():
        if isinstance(item, dict):
            collect_numeric_fields(item, fields)
        elif (
            isinstance(item, (int, float))
            and not isinstance(item, bool)
            and math.isfinite(item)
        ):
            fields[key].append(float(item))


def calculate_statistics(values):
    mean = fmean(values)
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean,
        "avg": mean,
        "std": pstdev(values),
    }


def build_physical_stability_report(statistics):
    physical_statistics = statistics.get("PhysicalPrintData", {})
    fields = (
        "bleedScore",
        "lineContinuity",
        "dotCircularity",
        "edgeTurbulence",
        "localVariance",
    )

    report = {}
    for field_name in fields:
        field_statistics = physical_statistics.get(field_name)
        if not field_statistics:
            continue

        mean = field_statistics["mean"]
        std = field_statistics["std"]
        report[f"{field_name}Std"] = std
        report[f"{field_name}CV"] = std / mean if mean != 0 else None

    return report


def dataAnalyzer(folder_path=FOLDER_PATH, output_path=OUTPUT_PATH):
    folder_path = Path(folder_path)
    output_path = Path(output_path)
    section_values = defaultdict(lambda: defaultdict(list))
    processed_files = []
    skipped_files = []

    for file_path in sorted(folder_path.glob("*.json")):
        # Do not include a previous result in the next calculation.
        if file_path.resolve() == output_path.resolve():
            continue

        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            skipped_files.append({"file": file_path.name, "reason": str(error)})
            continue

        if not isinstance(data, dict):
            skipped_files.append(
                {"file": file_path.name, "reason": "Top-level JSON is not an object"}
            )
            continue

        found_numeric_data = False
        for section_name, section_data in data.items():
            if section_name in {"metaData", "error"} or not isinstance(
                section_data, dict
            ):
                continue

            count_before = sum(
                len(values) for values in section_values[section_name].values()
            )
            collect_numeric_fields(section_data, section_values[section_name])
            count_after = sum(
                len(values) for values in section_values[section_name].values()
            )
            found_numeric_data = found_numeric_data or count_after > count_before

        if found_numeric_data:
            processed_files.append(file_path.name)
        else:
            skipped_files.append(
                {"file": file_path.name, "reason": "No numeric analysis data found"}
            )

    statistics = {
        section_name: {
            field_name: calculate_statistics(values)
            for field_name, values in sorted(fields.items())
            if values
        }
        for section_name, fields in sorted(section_values.items())
    }

    result = {
        "dataset": folder_path.name,
        "sourceFolder": str(folder_path),
        "processedFileCount": len(processed_files),
        "skippedFileCount": len(skipped_files),
        "statistics": statistics,
        "physicalStabilityReport": build_physical_stability_report(statistics),
        "skippedFiles": skipped_files,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, allow_nan=False)

    print(f"Processed {len(processed_files)} JSON files.")
    print(f"Skipped {len(skipped_files)} JSON files.")
    print(f"Summary written to: {output_path}")
    return result


if __name__ == "__main__":
    dataAnalyzer()
