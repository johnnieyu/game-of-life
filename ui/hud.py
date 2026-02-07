"""Heads-up display for game information."""
import pygame
from display.renderer import Renderer
from display.pixelfont import PixelFont
from engine.grid import Grid


class HUD:
    """Heads-up display showing game stats with retro pixel aesthetic."""

    def __init__(self):
        """Initialize HUD."""
        self.visible = True
        self.show_hints = True

        # Pixel fonts
        self.font_large = PixelFont(scale=2)
        self.font_small = PixelFont(scale=1)

        # Theme notification
        self.theme_notification = None
        self.theme_notification_timer = 0.0

    def notify_theme_change(self, theme_name: str):
        """Show a brief notification when theme changes."""
        self.theme_notification = theme_name.upper()
        self.theme_notification_timer = 2.0  # Show for 2 seconds

    def update(self, dt: float):
        """Update HUD timers."""
        if self.theme_notification_timer > 0:
            self.theme_notification_timer -= dt
            if self.theme_notification_timer <= 0:
                self.theme_notification = None

    def render(self, renderer: Renderer, grid: Grid, speed: int,
               state_name: str, controller_connected: bool = False):
        """
        Render the HUD.

        Args:
            renderer: Renderer instance
            grid: Game grid
            speed: Current simulation speed
            state_name: Current game state name
            controller_connected: Whether controller is connected
        """
        if not self.visible:
            return

        theme = renderer.theme
        screen = renderer.screen
        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # === TOP BAR ===
        self._render_top_bar(screen, screen_w, theme, grid, speed, state_name)

        # === BOTTOM HINTS ===
        if self.show_hints:
            self._render_hints(screen, screen_w, screen_h, theme,
                             state_name, controller_connected)

        # === THEME NOTIFICATION ===
        if self.theme_notification:
            self._render_theme_notification(screen, screen_w, screen_h, theme)

    def _render_top_bar(self, screen: pygame.Surface, screen_w: int,
                        theme, grid: Grid, speed: int, state_name: str):
        """Render the top information bar."""
        bar_height = 28
        padding = 8

        # Semi-transparent background bar
        bar_surface = pygame.Surface((screen_w, bar_height), pygame.SRCALPHA)
        bg = theme.hud_bg
        bar_surface.fill((bg[0], bg[1], bg[2], 200))
        screen.blit(bar_surface, (0, 0))

        # Bottom border line
        pygame.draw.line(screen, theme.text_dim,
                        (0, bar_height - 1), (screen_w, bar_height - 1))

        # Left side: Generation and Population
        gen_text = f"GEN {grid.generation:,}"
        gen_surface = self.font_large.render(gen_text, theme.title)
        screen.blit(gen_surface, (padding, 6))

        # Population after generation
        gen_width = gen_surface.get_width()
        pop_text = f"POP {grid.population():,}"
        pop_surface = self.font_large.render(pop_text, theme.text)
        screen.blit(pop_surface, (padding + gen_width + 20, 6))

        # Right side: Speed and State
        # State indicator (highlighted)
        state_text = state_name.upper()
        state_surface = self.font_large.render(state_text, theme.text_highlight)
        state_x = screen_w - padding - state_surface.get_width()
        screen.blit(state_surface, (state_x, 6))

        # Speed indicator
        speed_text = f"{speed} GEN/S"
        speed_surface = self.font_small.render(speed_text, theme.subtitle)
        speed_x = state_x - speed_surface.get_width() - 20
        screen.blit(speed_surface, (speed_x, 10))

        # Center: Small decorative separator dots
        center_x = screen_w // 2
        dot_color = theme.text_dim
        for i in range(-1, 2):
            pygame.draw.rect(screen, dot_color,
                           (center_x + i * 6, 12, 2, 2))

    def _render_hints(self, screen: pygame.Surface, screen_w: int, screen_h: int,
                      theme, state_name: str, controller_connected: bool):
        """Render control hints at bottom of screen."""
        hints = self._get_hints(state_name, controller_connected)

        if not hints:
            return

        bar_height = 22
        y = screen_h - bar_height

        # Semi-transparent background bar
        bar_surface = pygame.Surface((screen_w, bar_height), pygame.SRCALPHA)
        bg = theme.hud_bg
        bar_surface.fill((bg[0], bg[1], bg[2], 180))
        screen.blit(bar_surface, (0, y))

        # Top border line
        pygame.draw.line(screen, theme.text_dim, (0, y), (screen_w, y))

        # Render hints centered
        hint_text = "  |  ".join(hints)
        hint_surface = self.font_small.render(hint_text, theme.text_dim)
        hint_rect = hint_surface.get_rect(center=(screen_w // 2, y + bar_height // 2 + 1))
        screen.blit(hint_surface, hint_rect)

    def _get_hints(self, state_name: str, controller_connected: bool) -> list:
        """Get the appropriate hints for current state and input method."""
        if controller_connected:
            hints_map = {
                'running': ["A:PAUSE", "B:MENU", "Y:EDIT", "L/R:SPEED", "T:THEME"],
                'paused': ["A:RESUME", "B:MENU", "Y:EDIT", "X:STEP", "T:THEME"],
                'editor': ["A:PLACE", "B:EXIT", "Y:ROTATE", "SEL:PATTERNS"],
            }
        else:
            hints_map = {
                'running': ["SPACE:PAUSE", "ESC:MENU", "E:EDIT", "+/-:SPEED", "T:THEME"],
                'paused': ["SPACE:RESUME", "ESC:MENU", "E:EDIT", "N:STEP", "T:THEME"],
                'editor': ["ENTER:PLACE", "ESC:EXIT", "R:ROTATE", "P:PATTERNS"],
            }

        return hints_map.get(state_name, [])

    def _render_theme_notification(self, screen: pygame.Surface,
                                    screen_w: int, screen_h: int, theme):
        """Render theme change notification."""
        # Calculate fade based on timer
        alpha = min(255, int(self.theme_notification_timer * 255))

        # Notification box in center-top area
        text = f"THEME: {self.theme_notification}"
        text_surface = self.font_large.render(text, theme.title)

        box_width = text_surface.get_width() + 40
        box_height = 36
        box_x = (screen_w - box_width) // 2
        box_y = 50

        # Background
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        bg = theme.menu_bg
        box_surface.fill((bg[0], bg[1], bg[2], min(220, alpha)))
        screen.blit(box_surface, (box_x, box_y))

        # Border
        border_color = (*theme.title, min(255, alpha))
        border_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, border_color,
                        (0, 0, box_width, box_height), 2)
        screen.blit(border_surface, (box_x, box_y))

        # Text (with alpha)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(screen_w // 2, box_y + box_height // 2))
        screen.blit(text_surface, text_rect)

    def toggle_visibility(self):
        """Toggle HUD visibility."""
        self.visible = not self.visible

    def toggle_hints(self):
        """Toggle control hints visibility."""
        self.show_hints = not self.show_hints
