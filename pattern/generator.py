import random

import random

COLORS = [
    (255, 0, 0),     # Red
    (0, 200, 0),     # Green (dominant)
    (0, 120, 255),   # Blue
    (255, 200, 0)    # Yellow
]

def pick_color():
    return random.choices(
        COLORS,
        weights=[2, 5, 2, 1]   # green dominates
    )[0]

def generate_pattern_matrix(size, seed):
    random.seed(seed)
    matrix = [[None]*size for _ in range(size)]

    for i in range(size):
        for j in range(size):

            if i > 0 and j > 0 and random.random() < 0.7:
                matrix[i][j] = random.choice([
                    matrix[i-1][j],
                    matrix[i][j-1]
                ])
            else:
                matrix[i][j] = pick_color()

    return matrix