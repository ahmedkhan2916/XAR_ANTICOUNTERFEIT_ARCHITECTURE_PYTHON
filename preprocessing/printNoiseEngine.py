import cv2
import numpy as np
import json
import sys


def analyze_print_noise(image_path):

    # =========================
    # LOAD IMAGE
    # =========================

    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Image not found")

    # =========================
    # GRAYSCALE
    # =========================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # =========================
    # EDGE MAP
    # =========================

    edges = cv2.Canny(
        gray,
        80,
        180
    )

    # =========================
    # LAPLACIAN
    # Detect tiny print chaos
    # =========================

    laplacian = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    edge_noise = laplacian.std()

    # =========================
    # LOCAL GRAIN NOISE
    # =========================

    blurred = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    difference = cv2.absdiff(
        gray,
        blurred
    )

    grain_noise = np.mean(
        difference
    )

    # =========================
    # EDGE DENSITY
    # =========================

    edge_pixels = np.count_nonzero(
        edges
    )

    total_pixels = (
        edges.shape[0]
        *
        edges.shape[1]
    )

    edge_density = (
        edge_pixels /
        total_pixels
    )

    # =========================
    # MICRO VARIANCE
    # Tiny texture turbulence
    # =========================

    local_variance = np.var(
        gray
    )

    # =========================
    # FINAL RESULT
    # =========================

    result = {

        "edgeNoise":
            round(
                float(edge_noise),
                3
            ),

        "grainNoise":
            round(
                float(grain_noise),
                3
            ),

        "edgeDensity":
            round(
                float(edge_density),
                5
            ),

        "localVariance":
            round(
                float(local_variance),
                3
            )
    }

    return result


# =========================
# TESTING
# =========================

if __name__ == "__main__":

    

    image_path = sys.argv[1]

    result = analyze_print_noise(
        image_path
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )