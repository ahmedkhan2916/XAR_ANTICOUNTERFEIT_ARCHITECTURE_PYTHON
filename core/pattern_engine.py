# core/pattern_engine.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hashlib
from typing import List, Tuple


class PatternEngine:
    """
    Responsible for:
    - Structuring color sequence into matrix
    - Applying pattern validation rules
    - Generating pattern hash
    """

    def __init__(self, matrix_size: int = 5):
        self.matrix_size = matrix_size

    # 🔹 Step 1: Convert sequence → matrix
    def generate_matrix(self, color_sequence: List[str]) -> List[List[str]]:
        matrix = []
        idx = 0

        for i in range(self.matrix_size):
            row = []
            for j in range(self.matrix_size):
                if idx < len(color_sequence):
                    row.append(color_sequence[idx])
                else:
                    row.append("X")  # padding
                idx += 1
            matrix.append(row)

        return matrix

    # 🔹 Step 2: Apply rules
    def validate_pattern(self, matrix: List[List[str]]) -> Tuple[bool, List[str]]:
        issues = []
        valid = True

        # Rule 1: No more than 2 same colors consecutively in a row
        for i, row in enumerate(matrix):
            count = 1
            for j in range(1, len(row)):
                if row[j] == "X" or row[j - 1] == "X":
                    count = 1
                    continue
                if row[j] == row[j - 1]:
                    count += 1
                    if count >= 3:
                        valid = False
                        issues.append(f"Row {i}: 3 consecutive {row[j]}")
                else:
                    count = 1

        # Rule 2: Avoid full same column
        for col in range(len(matrix[0])):
            column_values = [row[col] for row in matrix if row[col] != "X"]
            if not column_values or len(column_values) < len(matrix):
                continue
            if len(set(column_values)) == 1:
                valid = False
                issues.append(f"Column {col}: all same ({column_values[0]})")

        return valid, issues

    # 🔹 Step 3: Pattern Hash
    def generate_pattern_hash(self, matrix: List[List[str]]) -> str:
        flat_string = "".join(["".join(row) for row in matrix])
        return hashlib.sha256(flat_string.encode()).hexdigest()

    # 🔹 Debug helper
    def print_matrix(self, matrix: List[List[str]]):
        for row in matrix:
            print(" ".join(row))
