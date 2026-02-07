"""Visual effects for retro 8-bit aesthetic."""
import pygame
import math
from typing import Tuple, Optional


class Effects:
    """Visual effects manager."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Scanline effect
        self.scanlines_enabled = False
        self._scanline_surface = None
        self._create_scanline_surface()

        # CRT vignette
        self.vignette_enabled = False
        self._vignette_surface = None
        self._create_vignette_surface()

        # Cell glow
        self.cell_glow_enabled = True
        self.cell_border_enabled = True

    def _create_scanline_surface(self):
        """Create scanline overlay."""
        self._scanline_surface = pygame.Surface(
            (self.screen_width, self.screen_height),
            pygame.SRCALPHA
        )
        # Draw horizontal lines every 2 pixels
        for y in range(0, self.screen_height, 2):
            pygame.draw.line(
                self._scanline_surface,
                (0, 0, 0, 40),  # Semi-transparent black
                (0, y),
                (self.screen_width, y)
            )

    def _create_vignette_surface(self):
        """Create CRT vignette effect."""
        self._vignette_surface = pygame.Surface(
            (self.screen_width, self.screen_height),
            pygame.SRCALPHA
        )
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)

        for y in range(self.screen_height):
            for x in range(self.screen_width):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                # Darken edges
                alpha = int((dist / max_dist) ** 1.5 * 100)
                alpha = min(alpha, 150)
                if alpha > 10:
                    self._vignette_surface.set_at((x, y), (0, 0, 0, alpha))

    def apply_scanlines(self, screen: pygame.Surface):
        """Apply scanline effect to screen."""
        if self.scanlines_enabled and self._scanline_surface:
            screen.blit(self._scanline_surface, (0, 0))

    def apply_vignette(self, screen: pygame.Surface):
        """Apply vignette effect to screen."""
        if self.vignette_enabled and self._vignette_surface:
            screen.blit(self._vignette_surface, (0, 0))

    def draw_cell_with_effects(self, screen: pygame.Surface, x: int, y: int,
                                cell_size: int, color: Tuple[int, int, int],
                                bg_color: Tuple[int, int, int] = (0, 0, 0)):
        """Draw a cell with glow and/or border effects."""
        if self.cell_glow_enabled and cell_size >= 2:
            # Draw glow (slightly larger, dimmer rectangle behind)
            glow_color = tuple(max(0, c // 3) for c in color)
            glow_rect = (x - 1, y - 1, cell_size + 2, cell_size + 2)
            pygame.draw.rect(screen, glow_color, glow_rect)

        if self.cell_border_enabled and cell_size >= 4:
            # Draw cell with dark border for chunky pixel look
            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))
            # Inner highlight (top-left)
            highlight = tuple(min(255, c + 40) for c in color)
            pygame.draw.line(screen, highlight, (x, y), (x + cell_size - 2, y))
            pygame.draw.line(screen, highlight, (x, y), (x, y + cell_size - 2))
            # Inner shadow (bottom-right)
            shadow = tuple(max(0, c - 60) for c in color)
            pygame.draw.line(screen, shadow, (x + cell_size - 1, y + 1),
                           (x + cell_size - 1, y + cell_size - 1))
            pygame.draw.line(screen, shadow, (x + 1, y + cell_size - 1),
                           (x + cell_size - 1, y + cell_size - 1))
        else:
            # Simple filled rectangle
            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

    def toggle_scanlines(self):
        """Toggle scanline effect."""
        self.scanlines_enabled = not self.scanlines_enabled
        return self.scanlines_enabled

    def toggle_vignette(self):
        """Toggle vignette effect."""
        self.vignette_enabled = not self.vignette_enabled
        return self.vignette_enabled

    def toggle_cell_glow(self):
        """Toggle cell glow effect."""
        self.cell_glow_enabled = not self.cell_glow_enabled
        return self.cell_glow_enabled


class ScreenTransition:
    """Handle screen transitions."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.progress = 0.0
        self.duration = 0.5  # seconds
        self.transition_type = 'fade'
        self._old_screen = None

    def start(self, old_screen: pygame.Surface, transition_type: str = 'fade'):
        """Start a transition."""
        self._old_screen = old_screen.copy()
        self.transition_type = transition_type
        self.progress = 0.0
        self.active = True

    def update(self, dt: float) -> bool:
        """Update transition. Returns True if still active."""
        if not self.active:
            return False

        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.active = False
            self._old_screen = None
            return False
        return True

    def render(self, screen: pygame.Surface, new_screen: pygame.Surface):
        """Render the transition effect."""
        if not self.active or not self._old_screen:
            return

        if self.transition_type == 'fade':
            # Crossfade
            screen.blit(new_screen, (0, 0))
            self._old_screen.set_alpha(int(255 * (1 - self.progress)))
            screen.blit(self._old_screen, (0, 0))

        elif self.transition_type == 'wipe_right':
            # Wipe from left to right
            x = int(self.screen_width * self.progress)
            screen.blit(self._old_screen, (0, 0))
            screen.blit(new_screen, (0, 0), (0, 0, x, self.screen_height))

        elif self.transition_type == 'cellular':
            # Cells spread across screen
            screen.blit(self._old_screen, (0, 0))
            cell_size = 8
            cells_x = self.screen_width // cell_size
            cells_y = self.screen_height // cell_size
            threshold = self.progress * 1.5  # Overshoot for full coverage

            for cy in range(cells_y + 1):
                for cx in range(cells_x + 1):
                    # Distance from center, normalized
                    dist = math.sqrt((cx - cells_x/2)**2 + (cy - cells_y/2)**2)
                    max_dist = math.sqrt((cells_x/2)**2 + (cells_y/2)**2)
                    if dist / max_dist < threshold:
                        rect = (cx * cell_size, cy * cell_size, cell_size, cell_size)
                        screen.blit(new_screen, rect, rect)
