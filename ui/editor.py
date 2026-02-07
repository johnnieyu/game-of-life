"""Pattern editor for placing and drawing cells."""
import numpy as np
from typing import Optional, Tuple
from engine.patterns import Pattern
from display.viewport import Viewport
import config


class Editor:
    """Cell editor with cursor and pattern placement."""

    def __init__(self, grid_width: int, grid_height: int):
        """
        Initialize editor.

        Args:
            grid_width: Grid width in cells
            grid_height: Grid height in cells
        """
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Cursor position (float for smooth movement)
        self.cursor_x = 0.0
        self.cursor_y = 0.0

        # Current pattern (None = single cell mode)
        self.current_pattern: Optional[Pattern] = None
        self.pattern_rotation = 0  # 0, 90, 180, 270

        # Drawing state
        self.is_drawing = False

        # Movement speed
        self.cursor_speed = config.CURSOR_SPEED

    @property
    def cursor_cell(self) -> Tuple[int, int]:
        """Get cursor position as integer cell coordinates."""
        return (int(self.cursor_x), int(self.cursor_y))

    def move_cursor(self, dx: float, dy: float, wrap: bool = True):
        """
        Move cursor by delta.

        Args:
            dx: Horizontal movement
            dy: Vertical movement
            wrap: Whether to wrap at grid edges
        """
        self.cursor_x += dx * self.cursor_speed
        self.cursor_y += dy * self.cursor_speed

        if wrap:
            self.cursor_x = self.cursor_x % self.grid_width
            self.cursor_y = self.cursor_y % self.grid_height
        else:
            self.cursor_x = max(0, min(self.cursor_x, self.grid_width - 1))
            self.cursor_y = max(0, min(self.cursor_y, self.grid_height - 1))

    def move_cursor_cells(self, dx: int, dy: int, wrap: bool = True):
        """Move cursor by whole cells."""
        self.cursor_x = int(self.cursor_x) + dx
        self.cursor_y = int(self.cursor_y) + dy

        if wrap:
            self.cursor_x = self.cursor_x % self.grid_width
            self.cursor_y = self.cursor_y % self.grid_height
        else:
            self.cursor_x = max(0, min(self.cursor_x, self.grid_width - 1))
            self.cursor_y = max(0, min(self.cursor_y, self.grid_height - 1))

    def set_cursor(self, x: int, y: int):
        """Set cursor to specific position."""
        self.cursor_x = float(x)
        self.cursor_y = float(y)

    def set_pattern(self, pattern: Optional[Pattern]):
        """Set current pattern for stamping."""
        self.current_pattern = pattern
        self.pattern_rotation = 0

    def rotate_pattern(self):
        """Rotate current pattern 90 degrees clockwise."""
        self.pattern_rotation = (self.pattern_rotation + 90) % 360

    def get_pattern_data(self) -> Optional[np.ndarray]:
        """Get current pattern data with rotation applied."""
        if self.current_pattern is None:
            return None

        data = self.current_pattern.data
        rotations = (self.pattern_rotation // 90) % 4
        return np.rot90(data, -rotations)

    def get_pattern_size(self) -> Tuple[int, int]:
        """Get current pattern size (width, height) with rotation."""
        if self.current_pattern is None:
            return (1, 1)

        data = self.get_pattern_data()
        return (data.shape[1], data.shape[0])

    def center_on_viewport(self, viewport: Viewport):
        """Center cursor on current viewport."""
        vx, vy, vw, vh = viewport.get_visible_region()
        self.cursor_x = float(vx + vw // 2)
        self.cursor_y = float(vy + vh // 2)

    def follow_viewport(self, viewport: Viewport):
        """Ensure cursor stays visible in viewport."""
        vx, vy, vw, vh = viewport.get_visible_region()

        margin = 2  # Keep cursor this many cells from edge

        # Adjust viewport to follow cursor if needed
        cx, cy = self.cursor_cell

        if cx < vx + margin:
            viewport.x = cx - margin
        elif cx >= vx + vw - margin:
            viewport.x = cx - vw + margin + 1

        if cy < vy + margin:
            viewport.y = cy - margin
        elif cy >= vy + vh - margin:
            viewport.y = cy - vh + margin + 1
