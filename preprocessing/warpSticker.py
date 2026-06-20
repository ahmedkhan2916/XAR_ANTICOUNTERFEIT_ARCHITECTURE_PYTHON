import cv2
import numpy as np


def warp_sticker(image, corners, output_size=800):
    """
    image: original image
    corners: dictionary containing:
        {
            "top_left": (x, y),
            "top_right": (x, y),
            "bottom_right": (x, y),
            "bottom_left": (x, y)
        }

    output_size: final square size
    """

    # =========================
    # SOURCE POINTS
    # =========================

    src_points = np.array([
        corners["top_left"],
        corners["top_right"],
        corners["bottom_right"],
        corners["bottom_left"]
    ], dtype=np.float32)

    # =========================
    # DESTINATION POINTS
    # =========================

    dst_points = np.array([
        [0, 0],
        [output_size - 1, 0],
        [output_size - 1, output_size - 1],
        [0, output_size - 1]
    ], dtype=np.float32)

    # =========================
    # HOMOGRAPHY MATRIX
    # =========================

    matrix = cv2.getPerspectiveTransform(
        src_points,
        dst_points
    )

    # =========================
    # WARP IMAGE
    # =========================

    warped = cv2.warpPerspective(
        image,
        matrix,
        (output_size, output_size)
    )

    return warped


# =========================================
# TESTING
# =========================================

if __name__ == "__main__":

    image = cv2.imread("test.jpg")

    # Example marker coordinates
    # Replace with YOUR detected coordinates later

    corners = {
        "top_left": (100, 100),
        "top_right": (700, 120),
        "bottom_right": (720, 700),
        "bottom_left": (90, 680)
    }

    warped = warp_sticker(image, corners)

    cv2.imwrite("warped_output.png", warped)

    print("Warped image saved:")
    print("warped_output.png")

    cv2.imshow("Warped Sticker", warped)

    cv2.waitKey(0)
    cv2.destroyAllWindows()