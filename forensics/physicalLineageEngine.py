import json
import math
import sys


# ============================================
# SAFE VALUE NORMALIZER
# ============================================

def normalize(value, min_val, max_val):

    if max_val - min_val == 0:
        return 0

    normalized = (value - min_val) / (max_val - min_val)

    return max(0, min(normalized, 1))


# ============================================
# RANGE CHECKER
# ============================================

def within_range(value, min_val, max_val):

    return min_val <= value <= max_val


# ============================================
# SCORE PHYSICAL BEHAVIOR
# ============================================

def score_physical_behavior(scan_data, expected_ranges):

    total_score = 0
    max_score = 0

    details = {}

    for key in expected_ranges:

        if key not in scan_data:
            continue

        expected = expected_ranges[key]

        value = scan_data[key]

        min_val = expected["min"]
        max_val = expected["max"]

        max_score += 100

        if within_range(value, min_val, max_val):

            score = 100

        else:

            distance = min(
                abs(value - min_val),
                abs(value - max_val)
            )

            tolerance = max_val - min_val

            penalty = normalize(distance, 0, tolerance * 2)

            score = max(0, 100 - penalty * 100)

        total_score += score

        details[key] = {
            "value": value,
            "expectedMin": min_val,
            "expectedMax": max_val,
            "score": round(score, 2)
        }

    if max_score == 0:
        return 0, details

    final_score = (total_score / max_score) * 100

    return round(final_score, 2), details


# ============================================
# SYNTHETIC RISK ANALYZER
# ============================================

def analyze_synthetic_risk(scan_data):

    risk = 0

    reasons = []

    # TOO PERFECT GEOMETRY
    if scan_data.get("moduleUniformity", 0) < 0.02:
        risk += 20
        reasons.append("geometry_too_perfect")

    # LOW TURBULENCE
    if scan_data.get("edgeTurbulence", 0) < 40:
        risk += 20
        reasons.append("low_edge_turbulence")

    # LOW CHAOS
    if scan_data.get("microChaos", 0) < 10:
        risk += 20
        reasons.append("missing_micro_chaos")

    # PERFECT CONTINUITY
    if scan_data.get("lineContinuity", 0) > 90:
        risk += 20
        reasons.append("too_perfect_continuity")

    # LOW REGION DIVERSITY
    if scan_data.get("regionalVariance", 0) < 15:
        risk += 20
        reasons.append("low_regional_variance")

    return {
        "syntheticRisk": risk,
        "reasons": reasons
    }


# ============================================
# FINAL VERDICT ENGINE
# ============================================

def generate_verdict(lineage_score, synthetic_risk):

    if lineage_score >= 80 and synthetic_risk <= 25:
        return "GENUINE"

    if lineage_score >= 55 and synthetic_risk <= 55:
        return "SUSPICIOUS"

    return "FAKE"


# ============================================
# MAIN ENGINE
# ============================================

def analyze_lineage(master_profile, scan_profile):

    expected_ranges = master_profile["expectedRanges"]

    lineage_score, details = score_physical_behavior(
        scan_profile,
        expected_ranges
    )

    synthetic_analysis = analyze_synthetic_risk(scan_profile)

    synthetic_risk = synthetic_analysis["syntheticRisk"]

    verdict = generate_verdict(
        lineage_score,
        synthetic_risk
    )

    return {

        "verdict": verdict,

        "lineageScore": lineage_score,

        "syntheticRisk": synthetic_risk,

        "syntheticReasons": synthetic_analysis["reasons"],

        "metricScores": details
    }


# ============================================
# LOAD JSON
# ============================================

def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================
# CLI
# ============================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(json.dumps({
            "error": "Usage: python physicalLineageEngine.py master.json scan.json"
        }, indent=4))

        sys.exit()

    master_path = sys.argv[1]
    scan_path = sys.argv[2]

    master_profile = load_json(master_path)

    scan_profile = load_json(scan_path)

    result = analyze_lineage(
        master_profile,
        scan_profile
    )

    print(json.dumps(result, indent=4))