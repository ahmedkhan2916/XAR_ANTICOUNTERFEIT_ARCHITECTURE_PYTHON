from PIL import Image, ImageDraw
import random


# 🔥 LOGICAL COLORS (FOR SYSTEM)
LOGIC_COLORS = ["G", "B", "Y", "R", "K"]

# 🔥 VISUAL COLORS (FOR IMAGE)
COLOR_MAP = {
    "G": (46, 204, 113),
    "B": (52, 152, 219),
    "Y": (241, 196, 15),
    "R": (231, 76, 60),
    "K": (0, 0, 0),
    "W": (255, 255, 255)
}


def pick_logic_color(rng):
    r = rng.random()
    if r < 0.55:
        return "G"
    elif r < 0.75:
        return "B"
    elif r < 0.90:
        return "Y"
    elif r < 0.97:
        return "R"
    else:
        return "K"


def draw_pattern(matrix, cell_size=20, seed=None):

    rng = random.Random(seed)

    size = len(matrix)
    img_size = size * cell_size

    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)

    margin_outer = int(size * 0.1)
    margin_inner = int(size * 0.2)

    diag_bias = rng.random()

    for i in range(size):
        for j in range(size):

            # -------------------------
            # ZONE
            # -------------------------
            if i < margin_outer or j < margin_outer or i >= size - margin_outer or j >= size - margin_outer:
                zone = "outer"
            elif i > margin_inner and j > margin_inner and i < size - margin_inner and j < size - margin_inner:
                zone = "inner"
            else:
                zone = "mid"

            # -------------------------
            # LOGIC COLOR (IMPORTANT)
            # -------------------------
            if zone == "outer":
                logic_color = "G" if rng.random() < 0.7 else pick_logic_color(rng)

            elif zone == "mid":
                if i > 0 and j > 0:
                    if rng.random() < 0.5:
                        logic_color = matrix[i-1][j]
                    else:
                        logic_color = matrix[i][j-1]
                else:
                    logic_color = pick_logic_color(rng)

            else:  # inner
                logic_color = pick_logic_color(rng) if rng.random() < 0.3 else "W"

            # -------------------------
            # DRAW VISUAL COLOR
            # -------------------------
            color = COLOR_MAP[logic_color]

            shrink = 4
            x1 = j * cell_size + shrink
            y1 = i * cell_size + shrink
            x2 = (j + 1) * cell_size - shrink
            y2 = (i + 1) * cell_size - shrink

            draw.rectangle([x1, y1, x2, y2], fill=color)

            # 🔥 STORE LOGIC COLOR (NOT HEX)
            matrix[i][j] = logic_color

    return img