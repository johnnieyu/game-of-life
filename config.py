"""Configuration settings for Conway's Game of Life."""

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FULLSCREEN = False

# Grid settings
CELL_SIZE = 2  # pixels per cell (1, 2, 4, 8)
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Virtual grid (can be larger than screen)
VIRTUAL_GRID_WIDTH = 1024
VIRTUAL_GRID_HEIGHT = 512

# Simulation settings
DEFAULT_SPEED = 10  # generations per second
MIN_SPEED = 1
MAX_SPEED = 60

# Wrap mode: 'toroidal' (wrapping) or 'bounded'
WRAP_MODE = 'toroidal'

# Display options
SHOW_GRID_LINES = False
GRID_LINE_COLOR = (40, 40, 40)

# Zoom levels (cell sizes in pixels)
ZOOM_LEVELS = [1, 2, 4, 8]
DEFAULT_ZOOM_INDEX = 1  # 2x zoom

# Controller settings
JOYSTICK_DEADZONE = 0.2
PAN_SPEED = 5  # cells per frame when panning
CURSOR_SPEED = 0.5  # cells per frame for smooth cursor movement

# Paths
import os
USER_PATTERNS_DIR = os.path.expanduser('~/conway/user_patterns')
BUILTIN_PATTERNS_DIR = os.path.join(os.path.dirname(__file__), 'patterns')

# Ensure user patterns directory exists
os.makedirs(USER_PATTERNS_DIR, exist_ok=True)
