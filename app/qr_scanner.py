try:
    import cv2
except ImportError as exc:
    raise ImportError(
        "The 'opencv-python' package is required. Install it with 'python -m pip install opencv-python'."
    ) from exc

try:
    from pyzbar.pyzbar import decode
except ImportError as exc:
    raise ImportError(
        "The 'pyzbar' package is required. Install it with 'python -m pip install pyzbar'."
    ) from exc


class QRScanner:
    def scan_from_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        decoded_objects = decode(img)
        if not decoded_objects:
            return None

        return decoded_objects[0].data.decode("utf-8")
