"""Menu state for main menu and submenus."""
import pygame
import random
from typing import Optional, List
from .state_machine import State
from ui.menu import Menu, MenuItem, PatternBrowser
from engine.patterns import PatternLoader
from display.themes import THEMES
from display.pixelfont import PixelFont
import config


class MenuState(State):
    """Main menu state."""

    @property
    def name(self) -> str:
        return "menu"

    def __init__(self, game):
        super().__init__(game)

        self.current_menu: Optional[Menu] = None
        self.main_menu: Optional[Menu] = None
        self.pattern_browser: Optional[PatternBrowser] = None

        # Pagination settings for pattern browser
        self.items_per_page = 8
        self.current_page = 0

        # Pixel fonts
        self.font_large = PixelFont(scale=3)
        self.font_medium = PixelFont(scale=2)
        self.font_small = PixelFont(scale=1)  # Smaller for descriptions

        # Stick navigation cooldown
        self.stick_nav_cooldown = 0.0

        # Animated stars background
        self.stars: List[List] = []  # [x, y, brightness, speed]
        self._init_stars()

        # Animation timer
        self.elapsed = 0.0

        self._build_menus()

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
            speed = random.uniform(0.5, 2.0)  # Twinkle speed
            phase = random.uniform(0, 6.28)   # Random phase offset
            self.stars.append([x, y, brightness, speed, phase])

    def _build_menus(self):
        """Build menu structure."""
        # Play submenu
        play_menu = Menu("Play", [
            MenuItem(
                "New Game",
                action=lambda: "new_game",
                description="Start with empty grid"
            ),
            MenuItem(
                "Random Fill",
                action=lambda: "random",
                description="Start with random cells"
            ),
            MenuItem(
                "Load Pattern",
                action=lambda: "patterns",
                description="Browse pattern library"
            ),
            MenuItem(
                "Resume",
                action=lambda: "resume",
                description="Continue current game"
            ),
            MenuItem(
                "Back",
                action=lambda: "back",
                description="Return to main menu"
            ),
        ])

        # Demo submenu
        demo_menu = Menu("Demo", [
            MenuItem(
                "Title Sequence",
                action=lambda: "boot",
                description="Watch the intro animation"
            ),
            MenuItem(
                "Gallery Mode",
                action=lambda: "gallery",
                description="Auto-cycle through patterns"
            ),
            MenuItem(
                "Back",
                action=lambda: "back",
                description="Return to main menu"
            ),
        ])

        # Settings submenu
        settings_menu = Menu("Settings", [
            MenuItem(
                "Theme",
                action=self._cycle_theme,
                description="Change color scheme"
            ),
            MenuItem(
                "Grid Lines",
                action=self._toggle_grid_lines,
                description="Toggle grid line display"
            ),
            MenuItem(
                "Wrap Mode",
                action=self._toggle_wrap_mode,
                description="Toggle edge wrapping"
            ),
            MenuItem(
                "Back",
                action=lambda: "back",
                description="Return to main menu"
            ),
        ])

        # Main menu
        self.main_menu = Menu("Metabolic Sublimes Potluck", [
            MenuItem(
                "Play",
                submenu=play_menu,
                description="Start or continue a game"
            ),
            MenuItem(
                "Information",
                action=lambda: "info",
                description="About the Game of Life"
            ),
            MenuItem(
                "Demo",
                submenu=demo_menu,
                description="Watch demo sequences"
            ),
            MenuItem(
                "Settings",
                submenu=settings_menu,
                description="Configure game options"
            ),
            MenuItem(
                "Colophon",
                action=lambda: "colophon",
                description="Credits and version info"
            ),
            MenuItem(
                "Quit",
                action=lambda: "quit",
                description="Exit the game"
            ),
        ])

    def _build_pattern_browser(self):
        """Build pattern browser menu."""
        # Get hardcoded builtin patterns
        patterns = [PatternLoader.get_builtin(name)
                   for name in PatternLoader.list_builtin()]
        patterns = [p for p in patterns if p is not None]
        seen = {p.name.lower().replace(' ', '_') for p in patterns}

        # Load .rle/.cells files from builtin patterns directory
        for p in PatternLoader.load_directory(config.BUILTIN_PATTERNS_DIR):
            key = p.name.lower().replace(' ', '_')
            if key not in seen:
                patterns.append(p)
                seen.add(key)

        # Add user patterns
        for p in PatternLoader.load_directory(config.USER_PATTERNS_DIR):
            key = p.name.lower().replace(' ', '_')
            if key not in seen:
                patterns.append(p)
                seen.add(key)

        self.pattern_browser = PatternBrowser(
            patterns,
            on_select=self._select_pattern
        )
        self.pattern_browser.parent = self.main_menu

    def _select_pattern(self, pattern):
        """Handle pattern selection."""
        self.game.editor.set_pattern(pattern)
        self.game.grid.clear()

        # Place pattern in center
        cx = self.game.grid.width // 2 - pattern.width // 2
        cy = self.game.grid.height // 2 - pattern.height // 2
        self.game.grid.load_pattern(pattern.data, cx, cy)

        self.game.viewport.center_on(
            self.game.grid.width // 2,
            self.game.grid.height // 2
        )

        return "running"

    def _cycle_theme(self):
        """Cycle through available themes."""
        theme_names = list(THEMES.keys())
        current_idx = 0

        for i, name in enumerate(theme_names):
            if THEMES[name] == self.game.renderer.theme:
                current_idx = i
                break

        next_idx = (current_idx + 1) % len(theme_names)
        self.game.renderer.set_theme(theme_names[next_idx])
        return None

    def _toggle_grid_lines(self):
        """Toggle grid line display."""
        self.game.renderer.show_grid_lines = not self.game.renderer.show_grid_lines
        return None

    def _toggle_wrap_mode(self):
        """Toggle wrap mode."""
        if self.game.grid.wrap_mode == 'toroidal':
            self.game.grid.wrap_mode = 'bounded'
        else:
            self.game.grid.wrap_mode = 'toroidal'
        return None

    def enter(self, prev_state=None):
        self.current_menu = self.main_menu
        self.current_menu.show()

        # Build pattern browser fresh each time
        self._build_pattern_browser()

    def exit(self, next_state=None):
        if self.current_menu:
            self.current_menu.hide()

    def update(self, dt: float):
        # Update animation timer
        self.elapsed += dt

        # Update controller state
        self.game.controller.update()

        # Tick cooldowns
        if self.stick_nav_cooldown > 0:
            self.stick_nav_cooldown -= dt

        # Controller navigation
        from input.controller import Button, Axis

        if self.game.controller.just_pressed(Button.DPAD_UP):
            self.current_menu.navigate_up()
            self._update_page_for_selection()
        elif self.game.controller.just_pressed(Button.DPAD_DOWN):
            self.current_menu.navigate_down()
            self._update_page_for_selection()
        elif self.game.controller.just_pressed(Button.A):
            self._handle_select()
        elif self.game.controller.just_pressed(Button.B):
            self._handle_back()

        # L3: Cycle theme
        if self.game.controller.just_pressed(Button.L3):
            self._cycle_theme()

        # Left stick navigation
        ly = self.game.controller.get_axis(Axis.LEFT_Y)
        if abs(ly) < 0.3:
            self.stick_nav_cooldown = 0
        elif self.stick_nav_cooldown <= 0:
            if ly < -0.5:
                self.current_menu.navigate_up()
                self._update_page_for_selection()
                self.stick_nav_cooldown = 0.25
            elif ly > 0.5:
                self.current_menu.navigate_down()
                self._update_page_for_selection()
                self.stick_nav_cooldown = 0.25

    def _update_page_for_selection(self):
        """Update current page to show the selected item."""
        if isinstance(self.current_menu, PatternBrowser):
            selected = self.current_menu.selected_index
            self.current_page = selected // self.items_per_page

    def _handle_select(self):
        """Handle menu selection."""
        result = self.current_menu.select()

        if isinstance(result, Menu):
            self.current_menu.hide()
            self.current_menu = result
            self.current_menu.show()
        elif result == "new_game":
            self.game.grid.clear()
            self.game.state_machine.change_state("running")
        elif result == "random":
            self.game.grid.randomize(0.3)
            self.game.state_machine.change_state("running")
        elif result == "patterns":
            self.current_menu.hide()
            self.current_menu = self.pattern_browser
            self.current_page = 0
            self.current_menu.show()
        elif result == "resume":
            self.game.state_machine.change_state("running")
        elif result == "quit":
            self.game.running = False
        elif result == "back":
            self._handle_back()
        elif result == "running":
            self.game.state_machine.change_state("running")
        elif result == "info":
            self.game.state_machine.change_state("info")
        elif result == "gallery":
            self.game.state_machine.change_state("gallery")
        elif result == "colophon":
            self.game.state_machine.change_state("colophon")
        elif result == "boot":
            self.game.state_machine.change_state("boot")

    def _handle_back(self):
        """Handle back navigation."""
        parent = self.current_menu.back()
        if parent:
            self.current_menu.hide()
            self.current_menu = parent
            self.current_menu.show()

    def render(self):
        renderer = self.game.renderer
        screen = renderer.screen
        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # Dark background
        screen.fill(self.theme.screen_bg)

        # Draw twinkling stars
        self._draw_stars(screen)

        # Render current menu with pixel font
        if self.current_menu:
            self._render_pixel_menu(screen, screen_w, screen_h)

        # Apply effects
        if hasattr(renderer, 'effects'):
            renderer.effects.apply_scanlines(screen)
            renderer.effects.apply_vignette(screen)

        renderer.flip()

    def _draw_stars(self, screen: pygame.Surface):
        """Draw twinkling stars background."""
        import math
        for star in self.stars:
            x, y, base_brightness, speed, phase = star
            # Calculate twinkling brightness
            twinkle = (math.sin(self.elapsed * speed + phase) + 1) / 2
            brightness = base_brightness * (0.3 + 0.7 * twinkle)

            # Use theme star colors
            if random.random() > 0.7:
                base = self.theme.star_secondary
            else:
                base = self.theme.star_primary
            color = (int(base[0] * brightness), int(base[1] * brightness), int(base[2] * brightness))

            size = 2 if brightness > 0.7 else 1
            pygame.draw.rect(screen, color, (int(x), int(y), size, size))

    def _render_pixel_menu(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        """Render menu with pixel font."""
        menu = self.current_menu
        if not menu or not menu.visible:
            return

        # Check if we're rendering the pattern browser
        if isinstance(menu, PatternBrowser):
            self._render_pattern_browser(screen, screen_w, screen_h)
            return

        # Menu layout - calculate vertical centering
        title_height = 21  # scale 3 * 7
        item_spacing = 32
        title_gap = 55  # Gap between title and first item
        num_items = len(menu.items)

        # Total content height
        content_height = title_height + title_gap + (num_items * item_spacing)

        # Center vertically (leave some room at bottom for description)
        start_y = (screen_h - content_height) // 2

        # Draw title
        title_surface = self.font_large.render_with_shadow(
            menu.title.upper(),
            self.theme.title,
            self.theme.title_shadow,
            2
        )
        title_rect = title_surface.get_rect(center=(screen_w // 2, start_y + title_height // 2))
        screen.blit(title_surface, title_rect)

        # Draw menu items
        items_start_y = start_y + title_height + title_gap

        for i, item in enumerate(menu.items):
            is_selected = i == menu.selected_index
            y = items_start_y + i * item_spacing

            if is_selected:
                # Draw selection indicator
                color = self.theme.text_highlight
                # Draw arrow
                arrow = self.font_medium.render(">", self.theme.text_highlight)
                screen.blit(arrow, (screen_w // 2 - 100, y))
            else:
                color = self.theme.text

            # Draw item label
            label_surface = self.font_medium.render(item.label.upper(), color)
            label_rect = label_surface.get_rect(center=(screen_w // 2, y + 7))
            screen.blit(label_surface, label_rect)

        # Draw description for selected item at very bottom
        if menu.selected_item and menu.selected_item.description:
            desc_y = screen_h - 25  # Closer to bottom
            desc_surface = self.font_small.render(
                menu.selected_item.description.upper(),
                self.theme.text_dim
            )
            desc_rect = desc_surface.get_rect(center=(screen_w // 2, desc_y))
            screen.blit(desc_surface, desc_rect)

    def _render_pattern_browser(self, screen: pygame.Surface, screen_w: int, screen_h: int):
        """Render pattern browser with pagination and preview."""
        menu = self.current_menu
        patterns = menu.patterns

        if not patterns:
            return

        # Layout constants
        title_height = 21
        item_spacing = 28
        title_gap = 40
        margin_top = 60
        margin_bottom = 80
        preview_width = 200
        preview_margin = 40

        # Calculate available space for list (left side)
        list_area_width = screen_w - preview_width - preview_margin * 2
        list_center_x = list_area_width // 2

        # Pagination
        total_items = len(menu.items)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        visible_items = menu.items[start_idx:end_idx]

        # Calculate vertical centering for visible items
        num_visible = len(visible_items)
        content_height = title_height + title_gap + (num_visible * item_spacing)
        start_y = margin_top

        # Draw title
        title_surface = self.font_large.render_with_shadow(
            menu.title.upper(),
            self.theme.title,
            self.theme.title_shadow,
            2
        )
        title_rect = title_surface.get_rect(center=(list_center_x, start_y + title_height // 2))
        screen.blit(title_surface, title_rect)

        # Draw menu items
        items_start_y = start_y + title_height + title_gap

        for i, item in enumerate(visible_items):
            actual_index = start_idx + i
            is_selected = actual_index == menu.selected_index
            y = items_start_y + i * item_spacing

            if is_selected:
                color = self.theme.text_highlight
                arrow = self.font_medium.render(">", self.theme.text_highlight)
                screen.blit(arrow, (list_center_x - 120, y))
            else:
                color = self.theme.text

            label_surface = self.font_medium.render(item.label.upper(), color)
            label_rect = label_surface.get_rect(center=(list_center_x, y + 7))
            screen.blit(label_surface, label_rect)

        # Draw pagination info
        if total_pages > 1:
            page_text = f"PAGE {self.current_page + 1}/{total_pages}"
            page_surface = self.font_small.render(page_text, self.theme.subtitle)
            page_rect = page_surface.get_rect(center=(list_center_x, screen_h - 50))
            screen.blit(page_surface, page_rect)

        # Draw description for selected item
        if menu.selected_item and menu.selected_item.description:
            desc_y = screen_h - 25
            desc_surface = self.font_small.render(
                menu.selected_item.description.upper(),
                self.theme.text_dim
            )
            desc_rect = desc_surface.get_rect(center=(list_center_x, desc_y))
            screen.blit(desc_surface, desc_rect)

        # Draw pattern preview on the right
        self._render_pattern_preview(screen, screen_w, screen_h, preview_width, preview_margin)

    def _render_pattern_preview(self, screen: pygame.Surface, screen_w: int, screen_h: int,
                                 preview_width: int, preview_margin: int):
        """Render the pattern preview on the right side."""
        menu = self.current_menu
        if not hasattr(menu, 'patterns') or not menu.patterns:
            return

        pattern = menu.patterns[menu.selected_index]

        # Preview area position
        preview_x = screen_w - preview_width - preview_margin
        preview_y = 80
        preview_box_size = 160

        # Draw preview box background
        box_surface = pygame.Surface((preview_box_size + 20, preview_box_size + 20), pygame.SRCALPHA)
        bg = self.theme.menu_bg
        box_surface.fill((bg[0], bg[1], bg[2], 200))
        screen.blit(box_surface, (preview_x - 10, preview_y - 10))

        # Draw border
        pygame.draw.rect(screen, self.theme.text_dim,
                        (preview_x - 10, preview_y - 10, preview_box_size + 20, preview_box_size + 20), 2)

        # Draw pattern
        data = pattern.data
        h, w = data.shape

        # Calculate scale to fit in preview box
        scale = min(preview_box_size // max(w, 1), preview_box_size // max(h, 1), 8)
        scale = max(1, scale)

        offset_x = preview_x + (preview_box_size - w * scale) // 2
        offset_y = preview_y + (preview_box_size - h * scale) // 2

        cell_color = self.theme.cell_alive

        for row in range(h):
            for col in range(w):
                if data[row, col]:
                    pygame.draw.rect(
                        screen,
                        cell_color,
                        (offset_x + col * scale,
                         offset_y + row * scale,
                         scale - 1 if scale > 2 else scale,
                         scale - 1 if scale > 2 else scale)
                    )

        # Draw pattern name below preview
        name_surface = self.font_medium.render(pattern.name.upper(), self.theme.text)
        name_rect = name_surface.get_rect(center=(preview_x + preview_box_size // 2, preview_y + preview_box_size + 25))
        screen.blit(name_surface, name_rect)

        # Draw pattern dimensions
        dim_text = f"{w}X{h}"
        dim_surface = self.font_small.render(dim_text, self.theme.subtitle)
        dim_rect = dim_surface.get_rect(center=(preview_x + preview_box_size // 2, preview_y + preview_box_size + 50))
        screen.blit(dim_surface, dim_rect)

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._handle_back()
            elif event.key == pygame.K_b:
                self._handle_back()
            elif event.key == pygame.K_t:
                self._cycle_theme()
            elif event.key == pygame.K_UP:
                self.current_menu.navigate_up()
                self._update_page_for_selection()
            elif event.key == pygame.K_DOWN:
                self.current_menu.navigate_down()
                self._update_page_for_selection()
            elif event.key == pygame.K_RETURN:
                self._handle_select()

        return None
