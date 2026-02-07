"""Boot/splash screen state with animated title."""
import pygame
import random
import math
from typing import Optional, List, Tuple
from .state_machine import State
from display.pixelfont import PixelFont
from input.controller import Button


class BootState(State):
    """Animated boot screen with title sequence."""

    @property
    def name(self) -> str:
        return "boot"

    def __init__(self, game):
        super().__init__(game)

        # Pixel fonts at different scales
        self.font_xlarge = PixelFont(scale=6)  # Extra large for single word frames
        self.font_large = PixelFont(scale=4)
        self.font_medium = PixelFont(scale=3)
        self.font_small = PixelFont(scale=2)

        # Animation timing
        self.elapsed = 0.0
        self.phase = 0  # 0-3: word frames, 4: full title, 5: subtitle, 6: ready

        # Frame timings (seconds)
        self.frame_duration = 1.2  # Each word frame
        self.title_hold = 2.0     # Hold on full title
        self.fade_duration = 0.4

        # Animation cells (background effect)
        self.bg_cells: List[Tuple[int, int, float, float]] = []  # x, y, life, max_life
        self._init_bg_cells()

        # Twinkling stars
        self.stars: List[List] = []
        self._init_stars()

        # Glider animation
        self.glider_x = -50.0
        self.glider_y = 100.0
        self.glider_frame = 0
        self.glider_timer = 0.0

        # Skip flag
        self.skipped = False

    @property
    def theme(self):
        """Get current theme from renderer."""
        return self.game.renderer.theme

    def _init_bg_cells(self):
        """Initialize background cell animation."""
        self.bg_cells = []
        for _ in range(50):
            x = random.randint(0, self.game.renderer.screen_width)
            y = random.randint(0, self.game.renderer.screen_height)
            max_life = random.uniform(1.0, 3.0)
            life = random.uniform(0, max_life)
            self.bg_cells.append([x, y, life, max_life])

    def _init_stars(self):
        """Initialize twinkling stars background."""
        self.stars = []
        screen_w = self.game.renderer.screen_width
        screen_h = self.game.renderer.screen_height

        for _ in range(60):
            x = random.randint(0, screen_w)
            y = random.randint(0, screen_h)
            brightness = random.uniform(0.2, 1.0)
            speed = random.uniform(0.5, 2.0)
            phase = random.uniform(0, 6.28)
            self.stars.append([x, y, brightness, speed, phase])

    def enter(self, prev_state=None):
        self.elapsed = 0.0
        self.phase = 0
        self.skipped = False
        self.glider_x = -50.0
        self._init_bg_cells()

    def exit(self, next_state=None):
        pass

    def update(self, dt: float):
        self.elapsed += dt

        # Update phase based on elapsed time
        if not self.skipped:
            if self.elapsed < self.frame_duration:
                self.phase = 0  # "METABOLIC"
            elif self.elapsed < self.frame_duration * 2:
                self.phase = 1  # "SUBLIMES"
            elif self.elapsed < self.frame_duration * 3:
                self.phase = 2  # "POTLUCK"
            elif self.elapsed < self.frame_duration * 4:
                self.phase = 3  # All three words
            elif self.elapsed < self.frame_duration * 4 + self.title_hold:
                self.phase = 4  # Full title with subtitle
            else:
                self.phase = 5  # Ready to continue

        # Update controller
        self.game.controller.update()

        # Check for skip
        if (self.game.controller.just_pressed(Button.A) or
            self.game.controller.just_pressed(Button.START)):
            if self.phase < 5:
                self.skipped = True
                self.phase = 5
            else:
                self.game.state_machine.change_state("menu")

        # Update background cells
        for cell in self.bg_cells:
            cell[2] -= dt  # Decrease life
            if cell[2] <= 0:
                # Respawn cell
                cell[0] = random.randint(0, self.game.renderer.screen_width)
                cell[1] = random.randint(0, self.game.renderer.screen_height)
                cell[3] = random.uniform(1.0, 3.0)
                cell[2] = cell[3]

        # Update glider animation
        self.glider_timer += dt
        if self.glider_timer > 0.15:
            self.glider_timer = 0
            self.glider_frame = (self.glider_frame + 1) % 4
            self.glider_x += 8
            self.glider_y += 8

        if self.glider_x > self.game.renderer.screen_width + 50:
            self.glider_x = -50
            self.glider_y = random.randint(50, 150)

    def render(self):
        renderer = self.game.renderer
        screen = renderer.screen
        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # Clear with dark background
        screen.fill(self.theme.screen_bg)

        # Draw twinkling stars
        self._draw_stars(screen)

        # Draw animated background cells
        self._draw_bg_cells(screen)

        # Draw glider
        self._draw_glider(screen)

        # Draw title based on phase
        if self.phase == 0:
            self._draw_word_frame(screen, "METABOLIC", screen_w // 2, screen_h // 2)
        elif self.phase == 1:
            self._draw_word_frame(screen, "SUBLIMES", screen_w // 2, screen_h // 2)
        elif self.phase == 2:
            self._draw_word_frame(screen, "POTLUCK", screen_w // 2, screen_h // 2)
        elif self.phase >= 3:
            # Always use same layout (4 lines) to prevent shifting
            # Phase 3: three title words only
            # Phase 4+: include GAME OF LIFE subtitle
            self._draw_full_title(
                screen,
                screen_w // 2,
                screen_h // 2,
                include_subtitle=(self.phase >= 4)
            )

            if self.phase >= 5:
                # Draw "Press Start to Continue" with blink
                if int(self.elapsed * 2) % 2 == 0:
                    prompt_text = "PRESS START TO CONTINUE"
                    prompt = self.font_small.render(prompt_text, self.theme.text_dim)
                    prompt_rect = prompt.get_rect(center=(screen_w // 2, screen_h - 60))
                    screen.blit(prompt, prompt_rect)

        # Apply effects
        if hasattr(renderer, 'effects'):
            renderer.effects.apply_scanlines(screen)
            renderer.effects.apply_vignette(screen)

        renderer.flip()

    def _draw_word_frame(self, screen: pygame.Surface, word: str,
                         center_x: int, center_y: int):
        """Draw a single word extra large and centered."""
        # Calculate alpha based on phase timing
        phase_elapsed = self.elapsed % self.frame_duration
        if phase_elapsed < self.fade_duration:
            alpha = int(255 * (phase_elapsed / self.fade_duration))
        elif phase_elapsed > self.frame_duration - self.fade_duration:
            alpha = int(255 * ((self.frame_duration - phase_elapsed) / self.fade_duration))
        else:
            alpha = 255

        # Use extra large font for single word frames
        text_surface = self.font_xlarge.render_with_shadow(
            word, self.theme.title, self.theme.title_shadow, 4
        )
        text_surface.set_alpha(alpha)
        # Center on screen
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        screen.blit(text_surface, text_rect)

    def _draw_full_title(self, screen: pygame.Surface, center_x: int, center_y: int,
                         include_subtitle: bool = False):
        """Draw the full title with consistent spacing."""
        title_words = ["METABOLIC", "SUBLIMES", "POTLUCK"]
        spacing = 35

        # Always use 4-line layout to prevent shifting when subtitle appears
        start_y = center_y - (spacing * 1.5)  # 1.5 gaps above center

        for i, word in enumerate(title_words):
            text_surface = self.font_medium.render_with_shadow(
                word, self.theme.title, self.theme.title_shadow, 2
            )
            y = start_y + i * spacing
            text_rect = text_surface.get_rect(center=(center_x, y))
            screen.blit(text_surface, text_rect)

        # Only draw GAME OF LIFE when include_subtitle is True
        if include_subtitle:
            subtitle = self.font_medium.render_with_shadow(
                "GAME OF LIFE",
                self.theme.subtitle,
                self.theme.title_shadow,
                2
            )
            subtitle_y = start_y + 3 * spacing  # 4th line
            subtitle_rect = subtitle.get_rect(center=(center_x, subtitle_y))
            screen.blit(subtitle, subtitle_rect)

    def _draw_stars(self, screen: pygame.Surface):
        """Draw twinkling stars background."""
        import math
        for star in self.stars:
            x, y, base_brightness, speed, phase = star
            # Calculate twinkling brightness
            twinkle = (math.sin(self.elapsed * speed + phase) + 1) / 2
            brightness = base_brightness * (0.3 + 0.7 * twinkle)

            # Mix of primary and secondary star colors from theme
            if x % 3 == 0:
                base = self.theme.star_secondary
            else:
                base = self.theme.star_primary
            color = (int(base[0] * brightness), int(base[1] * brightness), int(base[2] * brightness))

            size = 2 if brightness > 0.7 else 1
            pygame.draw.rect(screen, color, (int(x), int(y), size, size))

    def _draw_bg_cells(self, screen: pygame.Surface):
        """Draw animated background cells."""
        base = self.theme.cell_alive
        for cell in self.bg_cells:
            x, y, life, max_life = cell
            # Fade based on life
            alpha = (life / max_life) * 0.3
            size = 4
            color = (int(base[0] * alpha), int(base[1] * alpha), int(base[2] * alpha))
            pygame.draw.rect(screen, color, (int(x), int(y), size, size))

    def _draw_glider(self, screen: pygame.Surface):
        """Draw animated glider."""
        # Glider patterns for 4 frames of animation
        glider_frames = [
            [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
            [(0, 1), (2, 0), (2, 1), (1, 2), (2, 2)],
            [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
            [(2, 0), (0, 1), (2, 1), (1, 2), (2, 2)],
        ]

        cell_size = 6
        pattern = glider_frames[self.glider_frame % 4]
        color = self.theme.cell_alive

        for dx, dy in pattern:
            x = int(self.glider_x + dx * cell_size)
            y = int(self.glider_y + dy * cell_size)
            pygame.draw.rect(screen, color, (x, y, cell_size - 1, cell_size - 1))

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.phase < 5:
                    self.skipped = True
                    self.phase = 5
                else:
                    return "menu"
            elif event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_t:
                self.game.renderer.cycle_theme()

        return None
