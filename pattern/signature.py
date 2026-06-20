def apply_signature(matrix):
    size = len(matrix)

    for i in range(size):
        matrix[i][i] = (20, 20, 20)  # dark grey (not black)

    return matrix