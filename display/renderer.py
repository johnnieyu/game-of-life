"""Pygame rendering for Game of Life."""
import pygame
import numpy as np
from typing import Optional, Tuple, List

from .viewport import Viewport
from .themes import Theme, THEMES, DEFAULT_THEME
from .effects import Effects, ScreenTransition
from engine.grid import Grid
from settings import settings
import config


class Renderer:
    """Handles all pygame rendering."""

    def __init__(self, fullscreen: bool = False):
        """Initialize the renderer."""
        pygame.init()

        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT

        flags = pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            flags
        )
        pygame.display.set_caption("Metabolic Sublimes Potluck: Game of Life")

        # Load theme from settings (or default)
        saved_theme = settings.get('theme', DEFAULT_THEME)
        self.theme = THEMES.get(saved_theme, THEMES[DEFAULT_THEME])

        # Font for UI
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)

        # Pre-render surfaces for performance
        self._cell_surfaces = {}

        # Grid lines toggle
        self.show_grid_lines = config.SHOW_GRID_LINES

        # Visual effects
        self.effects = Effects(self.screen_width, self.screen_height)
        self.transition = ScreenTransition(self.screen_width, self.screen_height)

        # Load effects settings
        self.effects.scanlines_enabled = settings.get('scanlines', False)
        self.effects.vignette_enabled = settings.get('vignette', False)
        self.effects.cell_glow_enabled = settings.get('cell_glow', True)
        self.effects.cell_border_enabled = settings.get('cell_border', True)

    def set_theme(self, theme_name: str):
        """Set the color theme."""
        if theme_name in THEMES:
            self.theme = THEMES[theme_name]
            self._cell_surfaces.clear()  # Clear cached surfaces

    def cycle_theme(self) -> str:
        """Cycle to the next color theme. Returns new theme name."""
        theme_names = list(THEMES.keys())
        current_idx = 0
        for i, name in enumerate(theme_names):
            if THEMES[name] == self.theme:
                current_idx = i
                break
        next_idx = (current_idx + 1) % len(theme_names)
        next_name = theme_names[next_idx]
        self.set_theme(next_name)
        settings.set('theme', next_name)  # Persist the choice
        return self.theme.name

    def _get_cell_surface(self, cell_size: int, alive: bool) -> pygame.Surface:
        """Get or create a cached cell surface."""
        key = (cell_size, alive)
        if key not in self._cell_surfaces:
            surf = pygame.Surface((cell_size, cell_size))
            color = self.theme.cell_alive if alive else self.theme.cell_dead
            surf.fill(color)
            self._cell_surfaces[key] = surf
        return self._cell_surfaces[key]

    def clear(self):
        """Clear the screen."""
        self.screen.fill(self.theme.background)

    def render_grid(self, grid: Grid, viewport: Viewport):
        """Render the game grid."""
        cell_size = viewport.cell_size
        x, y, width, height = viewport.get_visible_region()

        # Get visible region of cells
        region = grid.get_region(x, y, width + 1, height + 1)

        # Check if effects are enabled
        use_effects = (self.effects.cell_glow_enabled or
                       self.effects.cell_border_enabled) and cell_size >= 4

        # Draw cells
        for row in range(min(height + 1, region.shape[0])):
            for col in range(min(width + 1, region.shape[1])):
                if region[row, col]:
                    screen_x = col * cell_size - int((viewport.x % 1) * cell_size)
                    screen_y = row * cell_size - int((viewport.y % 1) * cell_size)

                    if 0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height:
                        if use_effects:
                            self.effects.draw_cell_with_effects(
                                self.screen, screen_x, screen_y,
                                cell_size, self.theme.cell_alive,
                                self.theme.background
                            )
                        else:
                            pygame.draw.rect(
                                self.screen,
                                self.theme.cell_alive,
                                (screen_x, screen_y, cell_size, cell_size)
                            )

        # Draw grid lines if enabled
        if self.show_grid_lines and cell_size >= 4:
            self._draw_grid_lines(viewport)

    def _draw_grid_lines(self, viewport: Viewport):
        """Draw grid lines."""
        cell_size = viewport.cell_size
        offset_x = int((viewport.x % 1) * cell_size)
        offset_y = int((viewport.y % 1) * cell_size)

        # Vertical lines
        for x in range(0, self.screen_width + cell_size, cell_size):
            pygame.draw.line(
                self.screen,
                self.theme.grid_lines,
                (x - offset_x, 0),
                (x - offset_x, self.screen_height)
            )

        # Horizontal lines
        for y in range(0, self.screen_height + cell_size, cell_size):
            pygame.draw.line(
                self.screen,
                self.theme.grid_lines,
                (0, y - offset_y),
                (self.screen_width, y - offset_y)
            )

    def render_cursor(self, cursor_x: int, cursor_y: int, viewport: Viewport,
                      pattern_size: Tuple[int, int] = (1, 1)):
        """Render the editor cursor."""
        cell_size = viewport.cell_size
        screen_x, screen_y = viewport.cell_to_screen(cursor_x, cursor_y)

        width = pattern_size[0] * cell_size
        height = pattern_size[1] * cell_size

        # Draw cursor outline
        pygame.draw.rect(
            self.screen,
            self.theme.cursor,
            (screen_x, screen_y, width, height),
            2  # Border width
        )

    def render_pattern_preview(self, pattern_data: np.ndarray, cursor_x: int,
                               cursor_y: int, viewport: Viewport,
                               alpha: int = 128):
        """Render a semi-transparent pattern preview."""
        cell_size = viewport.cell_size
        base_x, base_y = viewport.cell_to_screen(cursor_x, cursor_y)

        h, w = pattern_data.shape

        # Create transparent surface
        preview = pygame.Surface((w * cell_size, h * cell_size), pygame.SRCALPHA)

        for row in range(h):
            for col in range(w):
                if pattern_data[row, col]:
                    color = (*self.theme.cell_alive, alpha)
                    pygame.draw.rect(
                        preview,
                        color,
                        (col * cell_size, row * cell_size, cell_size, cell_size)
                    )

        self.screen.blit(preview, (base_x, base_y))

    def render_text(self, text: str, x: int, y: int, size: str = 'small',
                    color: Optional[Tuple[int, int, int]] = None,
                    center: bool = False):
        """Render text on screen."""
        if color is None:
            color = self.theme.text

        font = {
            'small': self.font_small,
            'medium': self.font_medium,
            'large': self.font_large
        }.get(size, self.font_small)

        surface = font.render(text, True, color)

        if center:
            rect = surface.get_rect(center=(x, y))
            self.screen.blit(surface, rect)
        else:
            self.screen.blit(surface, (x, y))

        return surface.get_size()

    def render_box(self, x: int, y: int, width: int, height: int,
                   color: Optional[Tuple[int, int, int]] = None,
                   alpha: int = 200):
        """Render a semi-transparent box."""
        if color is None:
            color = self.theme.menu_bg

        box = pygame.Surface((width, height), pygame.SRCALPHA)
        box.fill((*color, alpha))
        self.screen.blit(box, (x, y))

    def flip(self, apply_effects: bool = True):
        """Update the display."""
        if apply_effects:
            self.effects.apply_scanlines(self.screen)
            self.effects.apply_vignette(self.screen)
        pygame.display.flip()

    def toggle_scanlines(self) -> bool:
        """Toggle scanline effect."""
        enabled = self.effects.toggle_scanlines()
        settings.set('scanlines', enabled)
        return enabled

    def toggle_vignette(self) -> bool:
        """Toggle vignette effect."""
        enabled = self.effects.toggle_vignette()
        settings.set('vignette', enabled)
        return enabled

    def toggle_cell_glow(self) -> bool:
        """Toggle cell glow effect."""
        enabled = self.effects.toggle_cell_glow()
        settings.set('cell_glow', enabled)
        return enabled

    def quit(self):
        """Clean up pygame."""
        pygame.quit()
