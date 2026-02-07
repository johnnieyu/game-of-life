"""Keyboard input handling."""
import pygame
from typing import Set


class KeyboardInput:
    """Handle keyboard input as controller fallback."""

    def __init__(self):
        """Initialize keyboard input."""
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()

    def update(self, events: list):
        """Update keyboard state from pygame events."""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key not in self.keys_pressed:
                    self.keys_just_pressed.add(event.key)
                self.keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_just_released.add(event.key)
                    self.keys_pressed.discard(event.key)

    def is_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return key in self.keys_pressed

    def just_pressed(self, key: int) -> bool:
        """Check if a key was just pressed this frame."""
        return key in self.keys_just_pressed

    def just_released(self, key: int) -> bool:
        """Check if a key was just released this frame."""
        return key in self.keys_just_released

    def get_direction(self):
        """Get movement direction from arrow keys as (dx, dy)."""
        dx = dy = 0

        if self.is_pressed(pygame.K_LEFT):
            dx -= 1
        if self.is_pressed(pygame.K_RIGHT):
            dx += 1
        if self.is_pressed(pygame.K_UP):
            dy -= 1
        if self.is_pressed(pygame.K_DOWN):
            dy += 1

        return dx, dy

    def get_direction_just_pressed(self):
        """Get direction from just-pressed arrow keys."""
        dx = dy = 0

        if self.just_pressed(pygame.K_LEFT):
            dx -= 1
        if self.just_pressed(pygame.K_RIGHT):
            dx += 1
        if self.just_pressed(pygame.K_UP):
            dy -= 1
        if self.just_pressed(pygame.K_DOWN):
            dy += 1

        return dx, dy
