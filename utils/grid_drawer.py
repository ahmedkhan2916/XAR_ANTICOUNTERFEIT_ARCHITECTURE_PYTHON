from PIL import Image, ImageDraw
import random

COLOR_MAP = {
    'R': (255, 60, 60),
    'G': (40, 180, 90),
    'B': (50, 120, 255),
    'Y': (255, 200, 60)
}

def draw_pattern_v3_2(matrix, hash_value, cell_size=20, filename="pattern_v3_2.png"):
    size = len(matrix)
    img_size = size * cell_size

    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)

    # deterministic randomness (same pattern always same shape)
    random.seed(int(hash_value[:8], 16))

    for i in range(size):
        for j in range(size):
            color = COLOR_MAP[matrix[i][j]]

            x = j * cell_size
            y = i * cell_size

            # 🔥 shrink factor → creates micro gaps
            shrink = random.uniform(2, 6)

            x1 = x + shrink
            y1 = y + shrink
            x2 = x + cell_size - shrink
            y2 = y + cell_size - shrink

            # 🔥 rounded corners
            radius = random.uniform(2, 6)

            draw.rounded_rectangle(
                [x1, y1, x2, y2],
                radius=radius,
                fill=color
            )

            # 🔥 fragile connector (only sometimes)
            if random.random() < 0.15:
                cx = x + cell_size // 2
                cy = y + cell_size // 2

                draw.line(
                    [(cx, cy), (cx + random.randint(-6, 6), cy + random.randint(-6, 6))],
                    fill=color,
                    width=1
                )

    img.save(filename)
    print("🔥 V3.2 pattern saved:", filename)