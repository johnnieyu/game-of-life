"""Information state displaying Game of Life rules with demonstrations."""
import pygame
import numpy as np
import random
import math
from typing import Optional, List, Tuple
from .state_machine import State
from display.pixelfont import PixelFont
from input.controller import Button
import config


class PatternDemo:
    """A mini simulation demonstrating a Game of Life pattern or rule."""

    def __init__(self, initial_state: np.ndarray, name: str, desc: str,
                 highlight_cell: Optional[Tuple[int, int]] = None,
                 max_frames: int = 0):
        """
        Args:
            initial_state: Starting grid
            name: Display name
            desc: Description text
            highlight_cell: Optional cell to highlight (for rules page)
            max_frames: Max frames before reset (0 = run forever until stable/loop detected)
        """
        self.initial_state = initial_state.copy()
        self.cells = initial_state.copy()
        self.name = name
        self.desc = desc
        self.highlight = highlight_cell
        self.max_frames = max_frames
        self.frame = 0
        self.history: List[bytes] = []  # For loop detection

    def reset(self):
        """Reset to initial state."""
        self.cells = self.initial_state.copy()
        self.frame = 0
        self.history = []

    def step(self):
        """Advance one generation."""
        # Check if we should reset
        if self.max_frames > 0 and self.frame >= self.max_frames - 1:
            self.reset()
            return

        # Store state for loop detection
        state_bytes = self.cells.tobytes()
        if state_bytes in self.history:
            # We've seen this state before - reset
            self.reset()
            return
        self.history.append(state_bytes)

        # Keep history bounded
        if len(self.history) > 100:
            self.history.pop(0)

        h, w = self.cells.shape
        # Count neighbors
        padded = np.pad(self.cells, 1, mode='constant', constant_values=0)
        neighbors = np.zeros_like(self.cells)
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbors += padded[1+dy:1+dy+h, 1+dx:1+dx+w]

        # Apply rules
        birth = (self.cells == 0) & (neighbors == 3)
        survive = (self.cells == 1) & ((neighbors == 2) | (neighbors == 3))
        self.cells = (birth | survive).astype(np.uint8)
        self.frame += 1


class InfoState(State):
    """Information screen showing rules and pattern types with demonstrations."""

    @property
    def name(self) -> str:
        return "info"

    def __init__(self, game):
        super().__init__(game)

        # Pixel fonts
        self.font_large = PixelFont(scale=3)
        self.font_medium = PixelFont(scale=2)
        self.font_small = PixelFont(scale=1)

        # Animated stars background
        self.stars: List[List] = []
        self._init_stars()

        # Animation timers
        self.elapsed = 0.0
        self.step_timer = 0.0
        self.step_interval = 1.0  # Seconds between steps

        # Pages
        self.current_page = 0
        self.page_titles = ["THE FOUR RULES", "PATTERN TYPES"]
        self.page_demos = [
            self._create_rule_demos(),
            self._create_pattern_demos(),
        ]

    @property
    def theme(self):
        """Get current theme from renderer."""
        return self.game.renderer.theme

    def _create_rule_demos(self) -> List[PatternDemo]:
        """Create the 4 rule demonstration grids."""
        demos = []

        # 1. Underpopulation: cell with <2 neighbors dies
        grid1 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid1, "UNDERPOPULATION",
                                 "FEWER THAN 2 NEIGHBORS: CELL DIES",
                                 highlight_cell=(1, 4), max_frames=2))

        # 2. Survival: cell with 2-3 neighbors survives
        grid2 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid2, "SURVIVAL",
                                 "2 OR 3 NEIGHBORS: CELL LIVES ON",
                                 highlight_cell=(1, 5), max_frames=2))

        # 3. Overpopulation: cell with >3 neighbors dies
        grid3 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid3, "OVERPOPULATION",
                                 "MORE THAN 3 NEIGHBORS: CELL DIES",
                                 highlight_cell=(2, 6), max_frames=2))

        # 4. Birth: empty cell with exactly 3 neighbors becomes alive
        grid4 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid4, "BIRTH",
                                 "EXACTLY 3 NEIGHBORS: NEW CELL IS BORN",
                                 highlight_cell=(2, 6), max_frames=2))

        return demos

    def _create_pattern_demos(self) -> List[PatternDemo]:
        """Create pattern type demonstrations."""
        demos = []

        # 1. Still Life - Block (never changes)
        grid1 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid1, "STILL LIFE",
                                 "STABLE PATTERNS THAT NEVER CHANGE"))

        # 2. Oscillator - Blinker (period 2)
        grid2 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid2, "OSCILLATOR",
                                 "PATTERNS THAT CYCLE REPEATEDLY"))

        # 3. Spaceship - Glider (moves diagonally)
        grid3 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid3, "SPACESHIP",
                                 "PATTERNS THAT MOVE ACROSS THE GRID"))

        # 4. Methuselah - R-pentomino (evolves for many generations)
        grid4 = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        demos.append(PatternDemo(grid4, "METHUSELAH",
                                 "SMALL PATTERNS WITH LONG EVOLUTIONS"))

        return demos

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
        self.step_timer = 0.0
        self.current_page = 0
        for page_demos in self.page_demos:
            for demo in page_demos:
                demo.reset()

    def exit(self, next_state=None):
        pass

    def _next_page(self):
        """Go to next page."""
        self.current_page = (self.current_page + 1) % len(self.page_demos)
        # Reset demos on new page
        for demo in self.page_demos[self.current_page]:
            demo.reset()
        self.step_timer = 0.0

    def _prev_page(self):
        """Go to previous page."""
        self.current_page = (self.current_page - 1) % len(self.page_demos)
        # Reset demos on new page
        for demo in self.page_demos[self.current_page]:
            demo.reset()
        self.step_timer = 0.0

    def update(self, dt: float):
        self.elapsed += dt
        self.step_timer += dt

        # Step current page demos periodically
        if self.step_timer >= self.step_interval:
            self.step_timer = 0.0
            for demo in self.page_demos[self.current_page]:
                demo.step()

        # Update controller state
        self.game.controller.update()

        # Check for back button
        if (self.game.controller.just_pressed(Button.B) or
            self.game.controller.just_pressed(Button.START)):
            self.game.state_machine.change_state("menu")

        # Page navigation
        if (self.game.controller.just_pressed(Button.DPAD_RIGHT) or
            self.game.controller.just_pressed(Button.R)):
            self._next_page()
        elif (self.game.controller.just_pressed(Button.DPAD_LEFT) or
              self.game.controller.just_pressed(Button.L)):
            self._prev_page()

    def render(self):
        renderer = self.game.renderer
        screen = renderer.screen
        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # Dark background
        screen.fill(self.theme.screen_bg)

        # Draw twinkling stars
        self._draw_stars(screen)

        # Draw title
        title = self.font_large.render_with_shadow(
            self.page_titles[self.current_page], self.theme.title, self.theme.title_shadow, 2
        )
        title_rect = title.get_rect(center=(screen_w // 2, 30))
        screen.blit(title, title_rect)

        # Draw 2x2 grid of demos
        self._render_demos(screen, screen_w, screen_h)

        # Draw page indicator
        page_text = f"PAGE {self.current_page + 1}/{len(self.page_demos)}"
        page_surf = self.font_small.render(page_text, self.theme.text_dim)
        screen.blit(page_surf, (15, screen_h - 20))

        # Draw navigation hint at bottom
        hint = self.font_small.render("LEFT/RIGHT: FLIP PAGE  |  B: BACK", self.theme.text_dim)
        hint_rect = hint.get_rect(center=(screen_w // 2, screen_h - 20))
        screen.blit(hint, hint_rect)

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

    def _render_demos(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        """Render the 2x2 grid of demonstrations."""
        demos = self.page_demos[self.current_page]

        # Calculate quadrant positions
        quad_w = screen_w // 2
        quad_h = (screen_h - 80) // 2  # Leave room for title and hint
        start_y = 60

        positions = [
            (0, start_y),                    # Top-left
            (quad_w, start_y),               # Top-right
            (0, start_y + quad_h),           # Bottom-left
            (quad_w, start_y + quad_h),      # Bottom-right
        ]

        for i, demo in enumerate(demos):
            if i < len(positions):
                qx, qy = positions[i]
                self._render_demo(screen, demo, qx, qy, quad_w, quad_h)

    def _render_demo(self, screen: pygame.Surface, demo: PatternDemo,
                     qx: int, qy: int, qw: int, qh: int):
        """Render a single demonstration in its quadrant."""
        # Draw name
        name_surf = self.font_medium.render(demo.name, self.theme.subtitle)
        name_rect = name_surf.get_rect(center=(qx + qw // 2, qy + 15))
        screen.blit(name_surf, name_rect)

        # Draw description
        desc_surf = self.font_small.render(demo.desc, self.theme.text)
        desc_rect = desc_surf.get_rect(center=(qx + qw // 2, qy + 35))
        screen.blit(desc_surf, desc_rect)

        # Draw the mini grid
        cell_size = 20
        grid_h, grid_w = demo.cells.shape
        grid_pixel_w = grid_w * cell_size
        grid_pixel_h = grid_h * cell_size

        # Center grid in remaining space
        grid_x = qx + (qw - grid_pixel_w) // 2
        grid_y = qy + 50 + (qh - 70 - grid_pixel_h) // 2

        # Draw grid background
        pygame.draw.rect(screen, self.theme.menu_bg,
                        (grid_x - 2, grid_y - 2, grid_pixel_w + 4, grid_pixel_h + 4))

        # Draw cells
        for row in range(grid_h):
            for col in range(grid_w):
                cx = grid_x + col * cell_size
                cy = grid_y + row * cell_size

                is_highlight = demo.highlight and (row == demo.highlight[0] and col == demo.highlight[1])
                is_alive = demo.cells[row, col]

                if is_highlight:
                    # Draw highlight border
                    pygame.draw.rect(screen, self.theme.cursor,
                                   (cx, cy, cell_size, cell_size), 2)
                    if is_alive:
                        pygame.draw.rect(screen, self.theme.cursor,
                                       (cx + 3, cy + 3, cell_size - 6, cell_size - 6))
                    else:
                        pygame.draw.rect(screen, self.theme.text_dim,
                                       (cx + 3, cy + 3, cell_size - 6, cell_size - 6))
                elif is_alive:
                    pygame.draw.rect(screen, self.theme.cell_alive,
                                   (cx + 2, cy + 2, cell_size - 4, cell_size - 4))
                else:
                    # Empty cell - just draw faint grid
                    pygame.draw.rect(screen, self.theme.grid_lines,
                                   (cx, cy, cell_size, cell_size), 1)

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_b):
                return "menu"
            elif event.key == pygame.K_RIGHT:
                self._next_page()
            elif event.key == pygame.K_LEFT:
                self._prev_page()
            elif event.key == pygame.K_t:
                self.game.renderer.cycle_theme()

        return None
