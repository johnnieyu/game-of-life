"""Colophon state displaying credits and version info."""
import pygame
import random
import math
import os
from typing import Optional, List, Tuple
from .state_machine import State
from display.pixelfont import PixelFont
from input.controller import Button
import config


class ColophonState(State):
    """Colophon screen with credits and version info."""

    @property
    def name(self) -> str:
        return "colophon"

    def __init__(self, game):
        super().__init__(game)

        # Pixel fonts
        self.font_large = PixelFont(scale=3)
        self.font_medium = PixelFont(scale=2)
        self.font_small = PixelFont(scale=1)

        # Animated stars background
        self.stars: List[List] = []
        self._init_stars()

        # Animation timer
        self.elapsed = 0.0

        # Scroll speed in pixels per second
        self.scroll_speed = 25

        # Load colophon content from markdown file
        self.content = self._load_content()

    def _load_content(self) -> List[Tuple[str, str]]:
        """Load colophon content from colophon.md file.

        Markdown format:
        - # Title -> title style (large font with shadow)
        - ## Heading -> heading style (medium font)
        - Regular text -> text style (small font)
        - Blank lines -> spacers
        """
        md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "colophon.md")

        if not os.path.exists(md_path):
            # Fallback to default content
            return [
                ("COLOPHON", "title"),
                ("", "spacer"),
                ("COLOPHON.MD NOT FOUND", "text"),
            ]

        content = []
        with open(md_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n\r")

                if line.startswith("# "):
                    # Title (h1)
                    content.append((line[2:].strip().upper(), "title"))
                    content.append(("", "spacer"))
                elif line.startswith("## "):
                    # Heading (h2)
                    content.append((line[3:].strip().upper(), "heading"))
                elif line.strip() == "":
                    # Blank line = spacer
                    content.append(("", "spacer"))
                else:
                    # Regular text
                    content.append((line.strip().upper(), "text"))

        return content

    @property
    def theme(self):
        """Get current theme from renderer."""
        return self.game.renderer.theme

    def _init_stars(self):
        """Initialize twinkling stars background."""
        self.stars = []
        screen_w = config.SCREEN_WIDTH
        screen_h = config.SCREEN_HEIGHT

        for _ in range(80):
            x = random.randint(0, screen_w)
            y = random.randint(0, screen_h)
            brightness = random.uniform(0.2, 1.0)
            speed = random.uniform(0.5, 2.0)
            phase = random.uniform(0, 6.28)
            self.stars.append([x, y, brightness, speed, phase])

    def enter(self, prev_state=None):
        self.elapsed = 0.0

    def exit(self, next_state=None):
        pass

    def update(self, dt: float):
        self.elapsed += dt

        # Update controller state
        self.game.controller.update()

        # Check for back button
        if (self.game.controller.just_pressed(Button.B) or
            self.game.controller.just_pressed(Button.START)):
            self.game.state_machine.change_state("menu")

    def render(self):
        renderer = self.game.renderer
        screen = renderer.screen
        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # Dark background
        screen.fill(self.theme.screen_bg)

        # Draw twinkling stars
        self._draw_stars(screen)

        # Render content
        self._render_content(screen, screen_w, screen_h)

        # Draw navigation hint at bottom
        if int(self.elapsed * 2) % 2 == 0:
            hint = self.font_small.render("PRESS B OR ESC TO RETURN", self.theme.text_dim)
            hint_rect = hint.get_rect(center=(screen_w // 2, screen_h - 25))
            screen.blit(hint, hint_rect)

        # Apply effects
        if hasattr(renderer, 'effects'):
            renderer.effects.apply_scanlines(screen)
            renderer.effects.apply_vignette(screen)

        renderer.flip()

    def _draw_stars(self, screen: pygame.Surface):
        """Draw twinkling stars background."""
        for star in self.stars:
            x, y, base_brightness, speed, phase = star
            twinkle = (math.sin(self.elapsed * speed + phase) + 1) / 2
            brightness = base_brightness * (0.3 + 0.7 * twinkle)

            if random.random() > 0.7:
                base = self.theme.star_secondary
            else:
                base = self.theme.star_primary
            color = (int(base[0] * brightness), int(base[1] * brightness), int(base[2] * brightness))

            size = 2 if brightness > 0.7 else 1
            pygame.draw.rect(screen, color, (int(x), int(y), size, size))

    def _render_content(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        """Render colophon content with scrolling credits effect."""
        line_spacing = 18
        title_extra_spacing = 30  # Extra space after title

        # Calculate scroll offset - start from bottom of screen, scroll upward
        scroll_offset = self.elapsed * self.scroll_speed
        y = screen_h - scroll_offset  # Start at bottom, move up over time

        for text, style in self.content:
            if style == "spacer":
                y += 10
                continue
            elif style == "title":
                surface = self.font_large.render_with_shadow(
                    text, self.theme.title, self.theme.title_shadow, 2
                )
                y += 5  # Extra space before title text
            elif style == "heading":
                surface = self.font_medium.render(text, self.theme.subtitle)
                y += 5  # Extra space before heading
            else:  # text
                surface = self.font_small.render(text, self.theme.text)

            # Only draw if on screen (with some margin)
            if -50 < y < screen_h + 50:
                rect = surface.get_rect(center=(screen_w // 2, y))
                screen.blit(surface, rect)

            y += line_spacing

            # Add extra spacing after title
            if style == "title":
                y += title_extra_spacing

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_b):
                return "menu"
            elif event.key == pygame.K_t:
                self.game.renderer.cycle_theme()

        return None
