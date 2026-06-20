import cv2
import numpy as np
import hashlib
import json
import sys


def generate_forensic_signature(image_path):

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

    edge_density = (
        np.count_nonzero(edges)
        /
        (
            edges.shape[0]
            *
            edges.shape[1]
        )
    )

    # =========================
    # LAPLACIAN CHAOS
    # =========================

    laplacian = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    edge_noise = laplacian.std()

    # =========================
    # MICRO TEXTURE
    # =========================

    blurred = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    texture_difference = cv2.absdiff(
        gray,
        blurred
    )

    micro_texture = np.mean(
        texture_difference
    )

    # =========================
    # LOCAL VARIANCE
    # =========================

    local_variance = np.var(
        gray
    )

    # =========================
    # ENTROPY
    # =========================

    histogram = cv2.calcHist(
        [gray],
        [0],
        None,
        [256],
        [0, 256]
    )

    histogram = histogram.ravel()

    histogram = (
        histogram
        /
        histogram.sum()
    )

    histogram = histogram[
        histogram > 0
    ]

    entropy = -np.sum(
        histogram
        *
        np.log2(histogram)
    )

    # =========================
    # RAW FORENSIC VECTOR
    # =========================

    forensic_vector = [

        round(float(edge_density), 6),

        round(float(edge_noise), 3),

        round(float(micro_texture), 3),

        round(float(local_variance), 3),

        round(float(entropy), 3)
    ]

    # =========================
    # HASHED SIGNATURE
    # =========================

    vector_string = json.dumps(
        forensic_vector
    )

    forensic_hash = hashlib.sha256(
        vector_string.encode()
    ).hexdigest()

    # =========================
    # FINAL OBJECT
    # =========================

    result = {

        "forensicVector":
            forensic_vector,

        "forensicHash":
            forensic_hash,

        "metrics": {

            "edgeDensity":
                round(float(edge_density), 6),

            "edgeNoise":
                round(float(edge_noise), 3),

            "microTexture":
                round(float(micro_texture), 3),

            "localVariance":
                round(float(local_variance), 3),

            "entropy":
                round(float(entropy), 3)
        }
    }

    return result


# =========================
# TEST
# =========================

if __name__ == "__main__":

    image_path = sys.argv[1]

    result = generate_forensic_signature(
        image_path
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )