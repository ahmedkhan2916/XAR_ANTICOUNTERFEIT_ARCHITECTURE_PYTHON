try:
    import qrcode
except ImportError as exc:
    raise ImportError(
        "The 'qrcode' package is required. Install it with 'python -m pip install qrcode pillow'."
    ) from exc


class QRGenerator:
    def generate_qr(self, payload, filename="qr.png"):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=4,
        )

        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)

        print(f"QR saved as {filename}")
