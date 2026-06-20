# qr/qr_with_pattern.py

from pathlib import Path

import qrcode
from PIL import Image


class QRWithPattern:
    def __init__(self, qr_size=240, border_cells=2):
        self.qr_size = qr_size
        self.border_cells = border_cells

    def generate_qr(self, payload):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=0,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        pixels = qr_image.load()

        for y in range(qr_image.height):
            for x in range(qr_image.width):
                red, green, blue, _ = pixels[x, y]
                if red > 245 and green > 245 and blue > 245:
                    pixels[x, y] = (255, 255, 255, 0)
                else:
                    pixels[x, y] = (0, 0, 0, 255)

        return qr_image.resize((self.qr_size, self.qr_size), Image.NEAREST)

    def add_clean_buffer(self, qr_img):
        buffer_px = max(8, self.qr_size // 18)
        canvas = Image.new(
            "RGBA",
            (qr_img.width + (buffer_px * 2), qr_img.height + (buffer_px * 2)),
            (255, 255, 255, 0)
        )

        buffer_draw = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        buffer_pixels = buffer_draw.load()

        for y in range(canvas.height):
            for x in range(canvas.width):
                buffer_pixels[x, y] = (255, 255, 255, 255)

        buffer_draw.paste(qr_img, (buffer_px, buffer_px), qr_img)
        return buffer_draw

    def combine(self, pattern_img, payload, cell_size, output="final_qr.png"):
        del cell_size

        qr_img = self.add_clean_buffer(self.generate_qr(payload))
        pattern_rgba = pattern_img.convert("RGBA")

        pw, ph = pattern_rgba.size
        qw, qh = qr_img.size
        x = (pw - qw) // 2
        y = (ph - qh) // 2

        pattern_rgba.paste(qr_img, (x, y), qr_img)

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pattern_rgba.convert("RGB").save(output_path)
        print(f"Final QR with pattern saved as {output_path}")
