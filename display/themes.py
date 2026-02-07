"""Color themes for the game."""
from dataclasses import dataclass
from typing import Tuple

Color = Tuple[int, int, int]


@dataclass
class Theme:
    """Color theme configuration."""
    name: str
    background: Color
    cell_alive: Color
    cell_dead: Color  # Usually same as background
    grid_lines: Color
    text: Color
    text_highlight: Color
    menu_bg: Color
    menu_highlight: Color
    cursor: Color
    hud_bg: Color
    # UI colors for menus and overlays
    title: Color              # Primary accent (titles, important elements)
    title_shadow: Color       # Shadow color for title text
    subtitle: Color           # Secondary accent (subtitles, info)
    text_dim: Color           # Dimmed text (hints, descriptions)
    screen_bg: Color          # Screen background for menus/overlays
    star_primary: Color       # Primary star/particle color
    star_secondary: Color     # Secondary star/particle color


THEMES = {
    'classic': Theme(
        name='Classic',
        background=(0, 0, 0),
        cell_alive=(0, 255, 0),
        cell_dead=(0, 0, 0),
        grid_lines=(30, 30, 30),
        text=(200, 200, 200),
        text_highlight=(0, 255, 0),
        menu_bg=(20, 20, 20),
        menu_highlight=(0, 100, 0),
        cursor=(255, 255, 0),
        hud_bg=(0, 0, 0),
        title=(0, 255, 0),
        title_shadow=(0, 80, 0),
        subtitle=(100, 255, 150),
        text_dim=(150, 150, 150),
        screen_bg=(5, 15, 5),
        star_primary=(0, 150, 50),
        star_secondary=(50, 200, 100),
    ),
    'amber': Theme(
        name='Amber',
        background=(0, 0, 0),
        cell_alive=(255, 176, 0),
        cell_dead=(0, 0, 0),
        grid_lines=(40, 30, 0),
        text=(255, 200, 100),
        text_highlight=(255, 176, 0),
        menu_bg=(20, 15, 0),
        menu_highlight=(80, 60, 0),
        cursor=(255, 255, 100),
        hud_bg=(0, 0, 0),
        title=(255, 150, 0),
        title_shadow=(80, 40, 0),
        subtitle=(100, 180, 255),
        text_dim=(150, 150, 150),
        screen_bg=(5, 5, 15),
        star_primary=(150, 100, 50),
        star_secondary=(100, 80, 150),
    ),
    'blue': Theme(
        name='Blue',
        background=(0, 0, 20),
        cell_alive=(100, 150, 255),
        cell_dead=(0, 0, 20),
        grid_lines=(20, 20, 50),
        text=(200, 220, 255),
        text_highlight=(100, 150, 255),
        menu_bg=(10, 10, 30),
        menu_highlight=(30, 50, 100),
        cursor=(255, 255, 100),
        hud_bg=(0, 0, 20),
        title=(100, 180, 255),
        title_shadow=(30, 60, 100),
        subtitle=(200, 150, 255),
        text_dim=(120, 140, 180),
        screen_bg=(5, 5, 25),
        star_primary=(80, 100, 180),
        star_secondary=(150, 100, 200),
    ),
    'white': Theme(
        name='White',
        background=(255, 255, 255),
        cell_alive=(0, 0, 0),
        cell_dead=(255, 255, 255),
        grid_lines=(220, 220, 220),
        text=(60, 60, 60),
        text_highlight=(0, 100, 200),
        menu_bg=(240, 240, 240),
        menu_highlight=(200, 220, 255),
        cursor=(255, 100, 100),
        hud_bg=(255, 255, 255),
        title=(0, 100, 200),
        title_shadow=(150, 180, 220),
        subtitle=(200, 100, 50),
        text_dim=(140, 140, 140),
        screen_bg=(245, 245, 250),
        star_primary=(180, 180, 200),
        star_secondary=(200, 180, 160),
    ),
    'matrix': Theme(
        name='Matrix',
        background=(0, 10, 0),
        cell_alive=(0, 255, 65),
        cell_dead=(0, 10, 0),
        grid_lines=(0, 30, 0),
        text=(0, 200, 50),
        text_highlight=(0, 255, 65),
        menu_bg=(0, 15, 0),
        menu_highlight=(0, 50, 0),
        cursor=(100, 255, 100),
        hud_bg=(0, 10, 0),
        title=(0, 255, 65),
        title_shadow=(0, 80, 20),
        subtitle=(100, 255, 150),
        text_dim=(0, 120, 40),
        screen_bg=(0, 8, 0),
        star_primary=(0, 100, 30),
        star_secondary=(0, 150, 50),
    ),
}

DEFAULT_THEME = 'classic'
