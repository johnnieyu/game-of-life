"""Gallery state for auto-cycling pattern demo."""
import pygame
import random
import math
from typing import Optional, List
from .state_machine import State
from display.pixelfont import PixelFont
from engine.patterns import PatternLoader, Pattern
from input.controller import Button
import config


class GalleryState(State):
    """Auto-cycling demo that displays patterns."""

    @property
    def name(self) -> str:
        return "gallery"

    def __init__(self, game):
        super().__init__(game)

        # Pixel fonts
        self.font_large = PixelFont(scale=3)
        self.font_medium = PixelFont(scale=2)
        self.font_small = PixelFont(scale=1)

        # Pattern cycling
        self.patterns: List[Pattern] = []
        self.current_index = 0
        self.cycle_time = 10.0  # seconds per pattern
        self.timer = 0.0

        # Animation
        self.elapsed = 0.0

        # Simulation state for the current pattern
        self.sim_timer = 0.0
        self.sim_speed = 10  # generations per second

    @property
    def theme(self):
        """Get current theme from renderer."""
        return self.game.renderer.theme

    def _load_patterns(self):
        """Load all available patterns."""
        self.patterns = []

        # Load builtin patterns
        for name in PatternLoader.list_builtin():
            pattern = PatternLoader.get_builtin(name)
            if pattern:
                self.patterns.append(pattern)

        # Load user patterns
        user_patterns = PatternLoader.load_directory(config.USER_PATTERNS_DIR)
        self.patterns.extend(user_patterns)

    def _load_current_pattern(self):
        """Load the current pattern onto the grid."""
        if not self.patterns:
            return

        pattern = self.patterns[self.current_index]

        # Clear the grid
        self.game.grid.clear()

        # Place pattern in center
        cx = self.game.grid.width // 2 - pattern.width // 2
        cy = self.game.grid.height // 2 - pattern.height // 2
        self.game.grid.load_pattern(pattern.data, cx, cy)

        # Set zoom based on pattern size (larger patterns need more zoom out)
        max_dim = max(pattern.width, pattern.height)
        if max_dim > 15:
            self.game.viewport.set_zoom(2)  # 4px cells for medium/large patterns
        else:
            self.game.viewport.set_zoom(3)  # 8px cells for small patterns

        # Center viewport on pattern
        self.game.viewport.center_on(
            self.game.grid.width // 2,
            self.game.grid.height // 2
        )

        # Reset simulation timer
        self.sim_timer = 0.0

    def _next_pattern(self):
        """Advance to the next pattern."""
        if not self.patterns:
            return

        self.current_index = (self.current_index + 1) % len(self.patterns)
        self._load_current_pattern()
        self.timer = 0.0

    def enter(self, prev_state=None):
        self.elapsed = 0.0
        self.timer = 0.0
        self.current_index = 0
        self._load_patterns()
        self._load_current_pattern()

    def exit(self, next_state=None):
        pass

    def update(self, dt: float):
        self.elapsed += dt
        self.timer += dt

        # Update controller state
        self.game.controller.update()

        # Check for exit
        if (self.game.controller.just_pressed(Button.B) or
            self.game.controller.just_pressed(Button.START)):
            self.game.state_machine.change_state("menu")
            return

        # Check for skip (A button)
        if self.game.controller.just_pressed(Button.A):
            self._next_pattern()
            return

        # Auto-advance pattern
        if self.timer >= self.cycle_time:
            self._next_pattern()

        # Run simulation (use while loop to catch up if needed)
        self.sim_timer += dt
        step_interval = 1.0 / self.sim_speed
        while self.sim_timer >= step_interval:
            self.game.grid.step()
            self.sim_timer -= step_interval

    def render(self):
        renderer = self.game.renderer
        screen = renderer.screen
        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # Clear and render grid (same pattern as RunningState)
        renderer.clear()
        renderer.render_grid(self.game.grid, self.game.viewport)

        # Draw HUD overlay
        self._draw_overlay(screen, screen_w, screen_h)

        # flip() handles effects internally
        renderer.flip()

    def _draw_overlay(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        """Draw pattern info overlay."""
        if not self.patterns:
            # No patterns message
            text = self.font_medium.render("NO PATTERNS AVAILABLE", self.theme.text)
            rect = text.get_rect(center=(screen_w // 2, screen_h // 2))
            screen.blit(text, rect)
            return

        pattern = self.patterns[self.current_index]

        # Semi-transparent background for text at top
        overlay_height = 50
        overlay = pygame.Surface((screen_w, overlay_height), pygame.SRCALPHA)
        bg = self.theme.hud_bg
        overlay.fill((bg[0], bg[1], bg[2], 180))
        screen.blit(overlay, (0, 0))

        # Pattern name
        name_text = self.font_medium.render(pattern.name.upper(), self.theme.title)
        screen.blit(name_text, (15, 8))

        # Pattern info (index / total)
        info_text = f"{self.current_index + 1}/{len(self.patterns)}"
        info = self.font_small.render(info_text, self.theme.subtitle)
        screen.blit(info, (screen_w - info.get_width() - 15, 10))

        # Description if available
        if pattern.description:
            desc = self.font_small.render(pattern.description.upper(), self.theme.text)
            screen.blit(desc, (15, 30))

        # Timer bar at bottom of overlay
        bar_y = overlay_height - 3
        bar_width = int((self.timer / self.cycle_time) * screen_w)
        pygame.draw.rect(screen, self.theme.cell_alive, (0, bar_y, bar_width, 3))

        # Hint at bottom of screen
        hint_overlay = pygame.Surface((screen_w, 30), pygame.SRCALPHA)
        hint_overlay.fill((bg[0], bg[1], bg[2], 150))
        screen.blit(hint_overlay, (0, screen_h - 30))

        hint = self.font_small.render("A: SKIP  |  B: EXIT  |  T: THEME", self.theme.text_dim)
        hint_rect = hint.get_rect(center=(screen_w // 2, screen_h - 15))
        screen.blit(hint, hint_rect)

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_SPACE:
                self._next_pattern()
            elif event.key == pygame.K_b:
                return "menu"
            elif event.key == pygame.K_t:
                self.game.renderer.cycle_theme()

        return None
