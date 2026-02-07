"""Grid class for Conway's Game of Life."""
import numpy as np
from typing import Tuple, Optional


class Grid:
    """2D grid for Game of Life simulation."""

    def __init__(self, width: int, height: int, wrap_mode: str = 'toroidal'):
        """
        Initialize the grid.

        Args:
            width: Grid width in cells
            height: Grid height in cells
            wrap_mode: 'toroidal' (wrapping) or 'bounded'
        """
        self.width = width
        self.height = height
        self.wrap_mode = wrap_mode
        self.cells = np.zeros((height, width), dtype=np.uint8)
        self.generation = 0

    def clear(self):
        """Clear all cells."""
        self.cells.fill(0)
        self.generation = 0

    def get_cell(self, x: int, y: int) -> bool:
        """Get cell state at position."""
        if self.wrap_mode == 'toroidal':
            x = x % self.width
            y = y % self.height
        elif not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return bool(self.cells[y, x])

    def set_cell(self, x: int, y: int, alive: bool = True):
        """Set cell state at position."""
        if self.wrap_mode == 'toroidal':
            x = x % self.width
            y = y % self.height
        elif not (0 <= x < self.width and 0 <= y < self.height):
            return
        self.cells[y, x] = 1 if alive else 0

    def toggle_cell(self, x: int, y: int):
        """Toggle cell state at position."""
        if self.wrap_mode == 'toroidal':
            x = x % self.width
            y = y % self.height
        elif not (0 <= x < self.width and 0 <= y < self.height):
            return
        self.cells[y, x] = 1 - self.cells[y, x]

    def count_neighbors(self) -> np.ndarray:
        """Count neighbors for all cells using numpy convolution."""
        # Pad array based on wrap mode
        if self.wrap_mode == 'toroidal':
            padded = np.pad(self.cells, 1, mode='wrap')
        else:
            padded = np.pad(self.cells, 1, mode='constant', constant_values=0)

        # Count neighbors by shifting and summing
        neighbors = np.zeros_like(self.cells, dtype=np.uint8)
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbors += padded[1+dy:1+dy+self.height, 1+dx:1+dx+self.width]

        return neighbors

    def step(self):
        """Advance simulation by one generation using B3/S23 rules."""
        neighbors = self.count_neighbors()

        # B3/S23 rules:
        # - Birth: dead cell with exactly 3 neighbors becomes alive
        # - Survival: live cell with 2 or 3 neighbors stays alive
        # - Death: all other cells die
        birth = (self.cells == 0) & (neighbors == 3)
        survive = (self.cells == 1) & ((neighbors == 2) | (neighbors == 3))

        self.cells = (birth | survive).astype(np.uint8)
        self.generation += 1

    def population(self) -> int:
        """Return count of living cells."""
        return int(np.sum(self.cells))

    def load_pattern(self, pattern_data: np.ndarray, x: int, y: int,
                     rotation: int = 0):
        """
        Load a pattern onto the grid.

        Args:
            pattern_data: 2D numpy array of pattern cells
            x, y: Top-left position to place pattern
            rotation: Rotation in degrees (0, 90, 180, 270)
        """
        # Apply rotation
        rotations = (rotation // 90) % 4
        data = np.rot90(pattern_data, -rotations)  # Negative for clockwise

        ph, pw = data.shape

        for py in range(ph):
            for px in range(pw):
                if data[py, px]:
                    self.set_cell(x + px, y + py, True)

    def get_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Get a region of the grid for rendering."""
        if self.wrap_mode == 'toroidal':
            # Handle wrapping for viewport
            result = np.zeros((height, width), dtype=np.uint8)
            for row in range(height):
                for col in range(width):
                    gx = (x + col) % self.width
                    gy = (y + row) % self.height
                    result[row, col] = self.cells[gy, gx]
            return result
        else:
            # Clamp to grid bounds
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(self.width, x + width)
            y2 = min(self.height, y + height)

            result = np.zeros((height, width), dtype=np.uint8)
            rx1 = x1 - x
            ry1 = y1 - y
            result[ry1:ry1+(y2-y1), rx1:rx1+(x2-x1)] = self.cells[y1:y2, x1:x2]
            return result

    def randomize(self, density: float = 0.3):
        """Fill grid with random cells."""
        self.cells = (np.random.random((self.height, self.width)) < density).astype(np.uint8)
        self.generation = 0
