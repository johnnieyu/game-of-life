"""Editor state - cell editing mode."""
import pygame
from typing import Optional
from .state_machine import State
from input.controller import Button
from ui.menu import PatternBrowser
from engine.patterns import PatternLoader
import config


class EditorState(State):
    """State for editing cells and placing patterns."""

    @property
    def name(self) -> str:
        return "editor"

    def __init__(self, game):
        super().__init__(game)
        self.pattern_browser: Optional[PatternBrowser] = None
        self.showing_patterns = False
        self.zoom_cooldown = 0.0

    def enter(self, prev_state=None):
        # Center cursor on viewport
        self.game.editor.center_on_viewport(self.game.viewport)
        self.showing_patterns = False

    def exit(self, next_state=None):
        self.showing_patterns = False
        if self.pattern_browser:
            self.pattern_browser.hide()

    def _build_pattern_browser(self):
        """Build pattern browser menu."""
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

    def _select_pattern(self, pattern):
        """Handle pattern selection."""
        self.game.editor.set_pattern(pattern)
        self.showing_patterns = False
        self.pattern_browser.hide()
        return None

    def update(self, dt: float):
        # Update controller state
        self.game.controller.update()

        # Tick cooldowns
        if self.zoom_cooldown > 0:
            self.zoom_cooldown -= dt

        # Update HUD timers
        self.game.hud.update(dt)

        if self.showing_patterns:
            self._handle_pattern_browser_input()
        else:
            self._handle_editor_input()

    def _handle_pattern_browser_input(self):
        """Handle input when pattern browser is open."""
        ctrl = self.game.controller

        if ctrl.just_pressed(Button.DPAD_UP):
            self.pattern_browser.navigate_up()
        elif ctrl.just_pressed(Button.DPAD_DOWN):
            self.pattern_browser.navigate_down()
        elif ctrl.just_pressed(Button.A):
            result = self.pattern_browser.select()
            if result is None:  # Pattern was selected via callback
                self.showing_patterns = False
        elif ctrl.just_pressed(Button.B):
            self.showing_patterns = False
            self.pattern_browser.hide()

    def _handle_editor_input(self):
        """Handle editor input."""
        ctrl = self.game.controller
        editor = self.game.editor

        # B button: Exit editor
        if ctrl.just_pressed(Button.B):
            self.game.state_machine.change_state("paused")
            return

        # A button: Place/toggle cell or pattern
        if ctrl.just_pressed(Button.A):
            self._place_or_toggle()

        # X button: Clear cell
        if ctrl.just_pressed(Button.X):
            cx, cy = editor.cursor_cell
            self.game.grid.set_cell(cx, cy, False)

        # Y button: Rotate pattern
        if ctrl.just_pressed(Button.Y):
            editor.rotate_pattern()

        # Select: Open pattern browser
        if ctrl.just_pressed(Button.SELECT):
            self._build_pattern_browser()
            self.pattern_browser.show()
            self.showing_patterns = True

        # Start: Exit editor and run
        if ctrl.just_pressed(Button.START):
            self.game.state_machine.change_state("running")
            return

        # D-pad: Move cursor by cells
        if ctrl.just_pressed(Button.DPAD_UP):
            editor.move_cursor_cells(0, -1)
        elif ctrl.just_pressed(Button.DPAD_DOWN):
            editor.move_cursor_cells(0, 1)
        elif ctrl.just_pressed(Button.DPAD_LEFT):
            editor.move_cursor_cells(-1, 0)
        elif ctrl.just_pressed(Button.DPAD_RIGHT):
            editor.move_cursor_cells(1, 0)

        # Left stick: Smooth cursor movement
        lx, ly = ctrl.get_left_stick()
        if lx != 0 or ly != 0:
            editor.move_cursor(lx * 3, ly * 3)

        # Right stick: Zoom (with cooldown)
        rx, ry = ctrl.get_right_stick()
        if self.zoom_cooldown <= 0:
            if ry < -0.5:
                self.game.viewport.zoom_in()
                self.zoom_cooldown = 0.3
            elif ry > 0.5:
                self.game.viewport.zoom_out()
                self.zoom_cooldown = 0.3

        # L3: Cycle theme
        if ctrl.just_pressed(Button.L3):
            theme_name = self.game.renderer.cycle_theme()
            self.game.hud.notify_theme_change(theme_name)

        # L/R: Prev/Next pattern
        if ctrl.just_pressed(Button.L):
            self._prev_pattern()
        if ctrl.just_pressed(Button.R):
            self._next_pattern()

        # Keep cursor visible
        editor.follow_viewport(self.game.viewport)

    def _place_or_toggle(self):
        """Place pattern or toggle single cell."""
        editor = self.game.editor
        cx, cy = editor.cursor_cell

        if editor.current_pattern:
            # Place pattern
            pattern_data = editor.get_pattern_data()
            self.game.grid.load_pattern(
                pattern_data,
                cx, cy,
                rotation=0  # Already rotated in get_pattern_data
            )
        else:
            # Toggle single cell
            self.game.grid.toggle_cell(cx, cy)

    def _prev_pattern(self):
        """Select previous pattern in library."""
        patterns = [PatternLoader.get_builtin(name)
                   for name in PatternLoader.list_builtin()]
        patterns = [p for p in patterns if p is not None]

        if not patterns:
            return

        current = self.game.editor.current_pattern
        if current is None:
            self.game.editor.set_pattern(patterns[-1])
        else:
            for i, p in enumerate(patterns):
                if p.name == current.name:
                    self.game.editor.set_pattern(patterns[i - 1])
                    return
            self.game.editor.set_pattern(patterns[-1])

    def _next_pattern(self):
        """Select next pattern in library."""
        patterns = [PatternLoader.get_builtin(name)
                   for name in PatternLoader.list_builtin()]
        patterns = [p for p in patterns if p is not None]

        if not patterns:
            return

        current = self.game.editor.current_pattern
        if current is None:
            self.game.editor.set_pattern(patterns[0])
        else:
            for i, p in enumerate(patterns):
                if p.name == current.name:
                    idx = (i + 1) % len(patterns)
                    self.game.editor.set_pattern(patterns[idx])
                    return
            self.game.editor.set_pattern(patterns[0])

    def render(self):
        self.game.renderer.clear()
        self.game.renderer.render_grid(self.game.grid, self.game.viewport)

        editor = self.game.editor
        cx, cy = editor.cursor_cell

        # Render pattern preview or cursor
        if editor.current_pattern:
            pattern_data = editor.get_pattern_data()
            self.game.renderer.render_pattern_preview(
                pattern_data,
                cx, cy,
                self.game.viewport
            )
            self.game.renderer.render_cursor(
                cx, cy,
                self.game.viewport,
                editor.get_pattern_size()
            )

            # Show pattern name
            self.game.renderer.render_box(
                self.game.renderer.screen_width // 2 - 100,
                10, 200, 30, alpha=180
            )
            self.game.renderer.render_text(
                f"Pattern: {editor.current_pattern.name}",
                self.game.renderer.screen_width // 2,
                20,
                size='small',
                center=True
            )
        else:
            self.game.renderer.render_cursor(
                cx, cy,
                self.game.viewport
            )

        # Render HUD
        # Get speed from running state
        running_state = self.game.state_machine.states.get('running')
        speed = running_state.speed if running_state else config.DEFAULT_SPEED

        self.game.hud.render(
            self.game.renderer,
            self.game.grid,
            speed,
            self.name,
            self.game.controller.connected
        )

        # Render pattern browser if open
        if self.showing_patterns and self.pattern_browser:
            # Dim background
            self.game.renderer.render_box(
                0, 0,
                self.game.renderer.screen_width,
                self.game.renderer.screen_height,
                color=(0, 0, 0),
                alpha=150
            )
            self.pattern_browser.render(self.game.renderer)

        self.game.renderer.flip()

    def handle_event(self, event) -> Optional[str]:
        if self.showing_patterns:
            return self._handle_pattern_browser_event(event)
        return self._handle_editor_event(event)

    def _handle_pattern_browser_event(self, event) -> Optional[str]:
        """Handle events when pattern browser is open."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.showing_patterns = False
                self.pattern_browser.hide()
            elif event.key == pygame.K_UP:
                self.pattern_browser.navigate_up()
            elif event.key == pygame.K_DOWN:
                self.pattern_browser.navigate_down()
            elif event.key == pygame.K_RETURN:
                self.pattern_browser.select()
                self.showing_patterns = False

        return None

    def _handle_editor_event(self, event) -> Optional[str]:
        """Handle events in editor mode."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "paused"
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._place_or_toggle()
            elif event.key == pygame.K_r:
                self.game.editor.rotate_pattern()
            elif event.key == pygame.K_p:
                self._build_pattern_browser()
                self.pattern_browser.show()
                self.showing_patterns = True
            elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                cx, cy = self.game.editor.cursor_cell
                self.game.grid.set_cell(cx, cy, False)
            elif event.key == pygame.K_c:
                self.game.editor.set_pattern(None)  # Clear pattern
            elif event.key == pygame.K_PAGEUP:
                self.game.viewport.zoom_in()
            elif event.key == pygame.K_PAGEDOWN:
                self.game.viewport.zoom_out()
            elif event.key == pygame.K_LEFTBRACKET:
                self._prev_pattern()
            elif event.key == pygame.K_RIGHTBRACKET:
                self._next_pattern()
            elif event.key == pygame.K_UP:
                self.game.editor.move_cursor_cells(0, -1)
            elif event.key == pygame.K_DOWN:
                self.game.editor.move_cursor_cells(0, 1)
            elif event.key == pygame.K_LEFT:
                self.game.editor.move_cursor_cells(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.game.editor.move_cursor_cells(1, 0)
            elif event.key == pygame.K_t:
                theme_name = self.game.renderer.cycle_theme()
                self.game.hud.notify_theme_change(theme_name)

        return None
