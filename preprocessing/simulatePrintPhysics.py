import cv2
import numpy as np


def simulate_print_physics(image):

    # -------------------------
    # VERY LIGHT blur
    # -------------------------
    softened = cv2.GaussianBlur(
        image,
        (3, 3),
        0.3
    )

    # -------------------------
    # Tiny printer texture noise
    # -------------------------
    noise = np.random.normal(
        0,
        1.2,
        softened.shape
    ).astype(np.int16)

    noisy = softened.astype(np.int16) + noise

    noisy = np.clip(
        noisy,
        0,
        255
    ).astype(np.uint8)

    # -------------------------
    # Very slight contrast softening
    # -------------------------
    final = cv2.convertScaleAbs(
        noisy,
        alpha=0.98,
        beta=1
    )

    return final