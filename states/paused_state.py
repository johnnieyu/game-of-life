"""Paused state - simulation paused with overlay."""
import pygame
from typing import Optional
from .state_machine import State
from input.controller import Button
import config


class PausedState(State):
    """State when simulation is paused."""

    @property
    def name(self) -> str:
        return "paused"

    def __init__(self, game):
        super().__init__(game)
        self.zoom_cooldown = 0.0

    def enter(self, prev_state=None):
        # Inherit speed from running state if available
        if prev_state and hasattr(prev_state, 'speed'):
            self._speed = prev_state.speed
        else:
            self._speed = config.DEFAULT_SPEED

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value
        # Sync back to running state
        running_state = self.game.state_machine.states.get('running')
        if running_state:
            running_state.speed = value

    def exit(self, next_state=None):
        pass

    def update(self, dt: float):
        # Update controller state
        self.game.controller.update()

        # Update HUD timers
        self.game.hud.update(dt)

        # Tick cooldowns
        if self.zoom_cooldown > 0:
            self.zoom_cooldown -= dt

        # Handle controller input
        self._handle_controller_input()

        # Handle keyboard panning
        self._handle_keyboard_pan()

    def _handle_keyboard_pan(self):
        """Handle keyboard panning with held keys."""
        keys = pygame.key.get_pressed()

        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= config.PAN_SPEED
        if keys[pygame.K_RIGHT]:
            dx += config.PAN_SPEED
        if keys[pygame.K_UP]:
            dy -= config.PAN_SPEED
        if keys[pygame.K_DOWN]:
            dy += config.PAN_SPEED

        if dx or dy:
            self.game.viewport.pan(dx, dy)

    def _handle_controller_input(self):
        """Handle controller input for paused state."""
        ctrl = self.game.controller

        # A button: Resume
        if ctrl.just_pressed(Button.A):
            self.game.state_machine.change_state("running")
            return

        # B button: Open menu
        if ctrl.just_pressed(Button.B):
            self.game.state_machine.change_state("menu")
            return

        # Y button: Toggle editor
        if ctrl.just_pressed(Button.Y):
            self.game.state_machine.change_state("editor")
            return

        # X button: Single step (no pan)
        if ctrl.just_pressed(Button.X):
            self.game.grid.step()

        # L/R: Adjust speed (for when resumed)
        if ctrl.just_pressed(Button.L):
            self.speed = max(config.MIN_SPEED, self.speed - 1)
        if ctrl.just_pressed(Button.R):
            self.speed = min(config.MAX_SPEED, self.speed + 1)

        # D-pad: Pan viewport
        if ctrl.just_pressed(Button.DPAD_UP):
            self.game.viewport.pan(0, -1)
        elif ctrl.just_pressed(Button.DPAD_DOWN):
            self.game.viewport.pan(0, 1)
        elif ctrl.just_pressed(Button.DPAD_LEFT):
            self.game.viewport.pan(-1, 0)
        elif ctrl.just_pressed(Button.DPAD_RIGHT):
            self.game.viewport.pan(1, 0)

        # Left stick: Pan viewport
        lx, ly = ctrl.get_left_stick()
        if lx != 0 or ly != 0:
            self.game.viewport.pan(
                lx * config.PAN_SPEED,
                ly * config.PAN_SPEED
            )

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

        # Start: Open menu
        if ctrl.just_pressed(Button.START):
            self.game.state_machine.change_state("menu")

        # Select: Reset/Clear
        if ctrl.just_pressed(Button.SELECT):
            self.game.grid.clear()

    def render(self):
        self.game.renderer.clear()
        self.game.renderer.render_grid(self.game.grid, self.game.viewport)

        self.game.hud.render(
            self.game.renderer,
            self.game.grid,
            self.speed,
            self.name,
            self.game.controller.connected
        )

        self.game.renderer.flip()

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_SPACE:
                return "running"
            elif event.key == pygame.K_e:
                return "editor"
            elif event.key == pygame.K_n:
                # Single step
                self.game.grid.step()
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                self.speed = min(config.MAX_SPEED, self.speed + 1)
            elif event.key == pygame.K_MINUS:
                self.speed = max(config.MIN_SPEED, self.speed - 1)
            elif event.key == pygame.K_c:
                self.game.grid.clear()
            elif event.key == pygame.K_h:
                self.game.hud.toggle_visibility()
            elif event.key == pygame.K_PAGEUP:
                self.game.viewport.zoom_in()
            elif event.key == pygame.K_PAGEDOWN:
                self.game.viewport.zoom_out()
            elif event.key == pygame.K_t:
                theme_name = self.game.renderer.cycle_theme()
                self.game.hud.notify_theme_change(theme_name)

        return None
