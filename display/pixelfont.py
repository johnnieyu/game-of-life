"""8-bit pixel font for retro aesthetic."""
import pygame
from typing import Tuple, Dict

# 5x7 pixel font data - each character is a list of 7 rows, each row is 5 bits
# Bit order: left to right (MSB to LSB in 5-bit space)
FONT_DATA: Dict[str, list] = {
    'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    'F': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    'G': [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
    'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'I': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111],
    'J': [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    'K': [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    'M': [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    'N': [0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'P': [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    'Q': [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    'R': [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    'S': [0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010],
    'X': [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    'Y': [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
    'Z': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    '0': [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111],
    '2': [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
    '3': [0b01110, 0b10001, 0b00001, 0b00110, 0b00001, 0b10001, 0b01110],
    '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    ':': [0b00000, 0b00100, 0b00100, 0b00000, 0b00100, 0b00100, 0b00000],
    '.': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100],
    ',': [0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
    '?': [0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0b00000, 0b00100],
    '-': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    '+': [0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
    '/': [0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000],
    '\'': [0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000],
}

# Character dimensions
CHAR_WIDTH = 5
CHAR_HEIGHT = 7


class PixelFont:
    """Retro 8-bit pixel font renderer."""

    def __init__(self, scale: int = 2):
        """
        Initialize pixel font.

        Args:
            scale: Pixel scale (1 = 5x7, 2 = 10x14, etc.)
        """
        self.scale = scale
        self._char_cache: Dict[Tuple[str, Tuple[int, int, int]], pygame.Surface] = {}

    def _render_char(self, char: str, color: Tuple[int, int, int]) -> pygame.Surface:
        """Render a single character to a surface."""
        cache_key = (char, color)
        if cache_key in self._char_cache:
            return self._char_cache[cache_key]

        width = CHAR_WIDTH * self.scale
        height = CHAR_HEIGHT * self.scale

        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        char_data = FONT_DATA.get(char.upper(), FONT_DATA.get(' '))
        if char_data is None:
            char_data = FONT_DATA[' ']

        for row_idx, row in enumerate(char_data):
            for col_idx in range(CHAR_WIDTH):
                # Check if bit is set (from left to right)
                if row & (1 << (CHAR_WIDTH - 1 - col_idx)):
                    x = col_idx * self.scale
                    y = row_idx * self.scale
                    pygame.draw.rect(surface, color,
                                   (x, y, self.scale, self.scale))

        self._char_cache[cache_key] = surface
        return surface

    def render(self, text: str, color: Tuple[int, int, int] = (255, 255, 255),
               spacing: int = 1) -> pygame.Surface:
        """
        Render text to a surface.

        Args:
            text: Text to render
            color: RGB color tuple
            spacing: Pixels between characters

        Returns:
            Surface containing rendered text
        """
        if not text:
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        char_width = CHAR_WIDTH * self.scale
        char_height = CHAR_HEIGHT * self.scale
        total_width = len(text) * char_width + (len(text) - 1) * spacing

        surface = pygame.Surface((total_width, char_height), pygame.SRCALPHA)

        x = 0
        for char in text:
            char_surface = self._render_char(char, color)
            surface.blit(char_surface, (x, 0))
            x += char_width + spacing

        return surface

    def render_with_shadow(self, text: str, color: Tuple[int, int, int],
                           shadow_color: Tuple[int, int, int] = (0, 0, 0),
                           shadow_offset: int = 2) -> pygame.Surface:
        """Render text with drop shadow."""
        char_width = CHAR_WIDTH * self.scale
        char_height = CHAR_HEIGHT * self.scale
        total_width = len(text) * char_width + (len(text) - 1) + shadow_offset

        surface = pygame.Surface((total_width, char_height + shadow_offset),
                                 pygame.SRCALPHA)

        # Render shadow
        shadow = self.render(text, shadow_color)
        surface.blit(shadow, (shadow_offset, shadow_offset))

        # Render main text
        main = self.render(text, color)
        surface.blit(main, (0, 0))

        return surface

    def get_size(self, text: str, spacing: int = 1) -> Tuple[int, int]:
        """Get the size of rendered text."""
        if not text:
            return (0, 0)
        char_width = CHAR_WIDTH * self.scale
        char_height = CHAR_HEIGHT * self.scale
        total_width = len(text) * char_width + (len(text) - 1) * spacing
        return (total_width, char_height)

    def clear_cache(self):
        """Clear the character cache."""
        self._char_cache.clear()
