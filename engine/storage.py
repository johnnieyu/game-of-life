"""Save and load patterns to/from files."""
import numpy as np
import os
from typing import Optional
from .patterns import Pattern


class PatternStorage:
    """Handle pattern file operations."""

    @staticmethod
    def to_rle(pattern: np.ndarray, name: str = "", author: str = "",
               description: str = "") -> str:
        """
        Convert a pattern array to RLE format.

        Args:
            pattern: 2D numpy array of cell states
            name: Pattern name
            author: Pattern author
            description: Pattern description

        Returns:
            RLE format string
        """
        lines = []

        # Metadata
        if name:
            lines.append(f"#N {name}")
        if author:
            lines.append(f"#O {author}")
        if description:
            # Split description into lines of ~70 chars
            words = description.split()
            current_line = "#C"
            for word in words:
                if len(current_line) + len(word) + 1 > 70:
                    lines.append(current_line)
                    current_line = "#C " + word
                else:
                    current_line += " " + word
            if current_line != "#C":
                lines.append(current_line)

        height, width = pattern.shape
        lines.append(f"x = {width}, y = {height}, rule = B3/S23")

        # Encode pattern
        rle_parts = []

        for y in range(height):
            row = pattern[y]
            x = 0
            row_parts = []

            while x < width:
                cell = row[x]
                char = 'o' if cell else 'b'

                # Count run length
                run = 1
                while x + run < width and row[x + run] == cell:
                    run += 1

                # Only encode dead cells if not at end of row
                if cell == 0:
                    # Skip trailing dead cells
                    if x + run >= width:
                        break

                if run > 1:
                    row_parts.append(f"{run}{char}")
                else:
                    row_parts.append(char)

                x += run

            rle_parts.append(''.join(row_parts))

        # Remove trailing empty rows
        while rle_parts and not rle_parts[-1]:
            rle_parts.pop()

        # Join rows with $ and end with !
        pattern_str = '$'.join(rle_parts) + '!'

        # Split into lines of ~70 chars
        current_line = ""
        for char in pattern_str:
            current_line += char
            if len(current_line) >= 70:
                lines.append(current_line)
                current_line = ""
        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

    @staticmethod
    def save_pattern(pattern: np.ndarray, filepath: str, name: str = "",
                     author: str = "", description: str = "") -> bool:
        """
        Save a pattern to a file.

        Args:
            pattern: 2D numpy array of cell states
            filepath: Path to save file
            name: Pattern name
            author: Pattern author
            description: Pattern description

        Returns:
            True if successful, False otherwise
        """
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Ensure .rle extension
        if not filepath.endswith('.rle'):
            filepath += '.rle'

        rle_content = PatternStorage.to_rle(pattern, name, author, description)

        with open(filepath, 'w') as f:
            f.write(rle_content)

        return True

    @staticmethod
    def extract_region(grid_cells: np.ndarray, x: int, y: int,
                       width: int, height: int) -> np.ndarray:
        """Extract a region from a grid for saving."""
        h, w = grid_cells.shape

        # Clamp bounds
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w, x + width)
        y2 = min(h, y + height)

        region = grid_cells[y1:y2, x1:x2].copy()

        # Trim empty rows and columns
        rows = np.any(region, axis=1)
        cols = np.any(region, axis=0)

        if not np.any(rows) or not np.any(cols):
            return np.zeros((1, 1), dtype=np.uint8)

        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]

        return region[y_min:y_max+1, x_min:x_max+1]
