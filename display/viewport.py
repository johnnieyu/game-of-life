"""Viewport handling for camera position and zoom."""
from typing import Tuple
import config


class Viewport:
    """Manages camera position and zoom level."""

    def __init__(self, grid_width: int, grid_height: int):
        """
        Initialize viewport.

        Args:
            grid_width: Total grid width in cells
            grid_height: Total grid height in cells
        """
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Camera position (top-left cell of viewport)
        self.x = 0.0
        self.y = 0.0

        # Zoom level
        self.zoom_levels = config.ZOOM_LEVELS
        self.zoom_index = config.DEFAULT_ZOOM_INDEX

        # Screen dimensions
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT

    @property
    def cell_size(self) -> int:
        """Current cell size in pixels."""
        return self.zoom_levels[self.zoom_index]

    @property
    def cells_wide(self) -> int:
        """Number of cells visible horizontally."""
        return self.screen_width // self.cell_size

    @property
    def cells_high(self) -> int:
        """Number of cells visible vertically."""
        return self.screen_height // self.cell_size

    def pan(self, dx: float, dy: float, wrap: bool = True):
        """
        Pan the viewport.

        Args:
            dx: Horizontal movement in cells
            dy: Vertical movement in cells
            wrap: Whether to wrap around grid edges
        """
        self.x += dx
        self.y += dy

        if wrap:
            self.x = self.x % self.grid_width
            self.y = self.y % self.grid_height
        else:
            # Clamp to grid bounds
            max_x = max(0, self.grid_width - self.cells_wide)
            max_y = max(0, self.grid_height - self.cells_high)
            self.x = max(0, min(self.x, max_x))
            self.y = max(0, min(self.y, max_y))

    def center_on(self, cell_x: int, cell_y: int):
        """Center viewport on a cell position."""
        self.x = cell_x - self.cells_wide // 2
        self.y = cell_y - self.cells_high // 2

    def zoom_in(self) -> bool:
        """
        Zoom in (increase cell size).

        Returns:
            True if zoom changed, False if already at max
        """
        if self.zoom_index < len(self.zoom_levels) - 1:
            # Get center point before zoom
            center_x = self.x + self.cells_wide / 2
            center_y = self.y + self.cells_high / 2

            self.zoom_index += 1

            # Re-center after zoom
            self.x = center_x - self.cells_wide / 2
            self.y = center_y - self.cells_high / 2
            return True
        return False

    def zoom_out(self) -> bool:
        """
        Zoom out (decrease cell size).

        Returns:
            True if zoom changed, False if already at min
        """
        if self.zoom_index > 0:
            # Get center point before zoom
            center_x = self.x + self.cells_wide / 2
            center_y = self.y + self.cells_high / 2

            self.zoom_index -= 1

            # Re-center after zoom
            self.x = center_x - self.cells_wide / 2
            self.y = center_y - self.cells_high / 2
            return True
        return False

    def set_zoom(self, index: int):
        """Set zoom to a specific level."""
        if 0 <= index < len(self.zoom_levels):
            self.zoom_index = index

    def screen_to_cell(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to cell coordinates."""
        cell_x = int(self.x) + screen_x // self.cell_size
        cell_y = int(self.y) + screen_y // self.cell_size
        return cell_x, cell_y

    def cell_to_screen(self, cell_x: int, cell_y: int) -> Tuple[int, int]:
        """Convert cell coordinates to screen coordinates."""
        screen_x = (cell_x - int(self.x)) * self.cell_size
        screen_y = (cell_y - int(self.y)) * self.cell_size
        return screen_x, screen_y

    def get_visible_region(self) -> Tuple[int, int, int, int]:
        """
        Get the region of cells currently visible.

        Returns:
            Tuple of (x, y, width, height) in cell coordinates
        """
        return (int(self.x), int(self.y), self.cells_wide, self.cells_high)

    def reset(self):
        """Reset viewport to initial position."""
        self.x = 0.0
        self.y = 0.0
        self.zoom_index = config.DEFAULT_ZOOM_INDEX
