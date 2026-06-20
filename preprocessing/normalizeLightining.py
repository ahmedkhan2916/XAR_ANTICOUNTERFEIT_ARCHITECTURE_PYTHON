import cv2
import numpy as np


def normalize_lighting(image_path, output_path="normalized.png"):

    # =========================
    # LOAD IMAGE
    # =========================

    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Image not found")

    # =========================
    # CONVERT TO GRAYSCALE
    # =========================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # =========================
    # LIGHTING NORMALIZATION
    # =========================

    background = cv2.GaussianBlur(
        gray,
        (0, 0),
        25
    )

    normalized = cv2.divide(
        gray,
        background,
        scale=255
    )

    # =========================
    # DETAIL-SAFE CONTRAST
    # =========================

    clahe = cv2.createCLAHE(
        clipLimit=1.8,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(normalized)

    contrast = cv2.normalize(
        contrast,
        None,
        alpha=0,
        beta=255,
        norm_type=cv2.NORM_MINMAX
    ).astype(np.uint8)

    sharp_reference = cv2.GaussianBlur(
        contrast,
        (0, 0),
        0.8
    )

    detail_preserved = cv2.addWeighted(
        contrast,
        1.35,
        sharp_reference,
        -0.35,
        0
    )

    # =========================
    # PHONE CAMERA DETAIL TUNING
    # =========================

    gamma = 1.25
    lookup_table = np.array(
        [255 * ((i / 255) ** gamma) for i in range(256)],
        dtype=np.uint8
    )

    camera_detail = cv2.LUT(
        detail_preserved,
        lookup_table
    )

    camera_detail = cv2.convertScaleAbs(
        camera_detail,
        alpha=1.1,
        beta=-10
    )

    # =========================
    # SAVE OUTPUT
    # =========================

    cv2.imwrite(
        output_path,
        camera_detail
    )

    print("here is normalized",output_path)
    return camera_detail,output_path


# =========================
# TESTING
# =========================

if __name__ == "__main__":

    result = normalize_lighting(
        "geminiSticker_XAR12345678_2.jpg",
        "geminiSticker_XAR12345678Completed_2.jpg"
    )

    print("Saved:")
    print("normalized_output6.png")

    cv2.imshow(
        "Normalized Image",
        result
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()
