import hashlib
from typing import Dict, List, Optional


class VirtualColorMapper:
    def __init__(self, secret_key: str, matrix_size: int = 5):
        """Convert binary data into a virtual color sequence."""
        self.secret_key = secret_key
        self.base_colors = ["R", "G", "B", "Y"]
        self.matrix_size = matrix_size

    def _generate_mapping(self, context: str) -> Dict[str, str]:
        """Build a deterministic color mapping from the secret and context."""
        seed_input = f"{self.secret_key}|{context}"
        seed_hash = hashlib.sha256(seed_input.encode()).hexdigest()

        colors = self.base_colors.copy()
        for index in range(len(colors)):
            swap_index = int(seed_hash[index], 16) % len(colors)
            colors[index], colors[swap_index] = colors[swap_index], colors[index]

        return {
            "00": colors[0],
            "01": colors[1],
            "10": colors[2],
            "11": colors[3],
        }

    def encode(self, binary_data: str, context: str) -> Dict[str, object]:
        """Convert only the provided binary string into virtual colors."""
        if not binary_data or not context:
            raise ValueError("Binary data and context must be provided.")
        if any(bit not in "01" for bit in binary_data):
            raise ValueError("Binary data must contain only 0 and 1.")

        normalized_binary = binary_data
        if len(normalized_binary) % 2 != 0:
            normalized_binary += "0"

        mapping = self._generate_mapping(context)
        color_sequence: List[str] = []
        for index in range(0, len(normalized_binary), 2):
            pair = normalized_binary[index : index + 2]
            color_sequence.append(mapping[pair])

        return {
            "colors": color_sequence,
            "mapping": mapping,
            "normalized_binary": normalized_binary,
            "original_length": len(binary_data),
        }

    def decode(
        self,
        color_sequence: List[str],
        mapping: Dict[str, str],
        original_length: Optional[int] = None,
    ) -> str:
        """Convert virtual color sequence back to binary string."""
        reverse_map = {value: key for key, value in mapping.items()}

        binary_output = ""
        for color in color_sequence:
            if color not in reverse_map:
                raise ValueError(f"Invalid color: {color}")
            binary_output += reverse_map[color]

        if original_length is None:
            return binary_output
        return binary_output[:original_length]
