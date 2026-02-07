"""Game controller input handling."""
import pygame
import json
import os
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto
import config


class Button(Enum):
    """Controller button mappings."""
    A = auto()
    B = auto()
    X = auto()
    Y = auto()
    START = auto()
    SELECT = auto()
    PLUS = auto()
    MINUS = auto()
    L = auto()
    R = auto()
    ZL = auto()
    ZR = auto()
    L3 = auto()
    R3 = auto()
    DPAD_UP = auto()
    DPAD_DOWN = auto()
    DPAD_LEFT = auto()
    DPAD_RIGHT = auto()


class Axis(Enum):
    """Controller axis mappings."""
    LEFT_X = auto()
    LEFT_Y = auto()
    RIGHT_X = auto()
    RIGHT_Y = auto()


@dataclass
class ControllerState:
    """Current state of the controller."""
    buttons: Dict[Button, bool]
    axes: Dict[Axis, float]
    connected: bool = False


# Default button mappings (used when no controller_map.json exists)
DEFAULT_BUTTON_MAP = {
    0: Button.A,      # A / Cross
    1: Button.B,      # B / Circle
    2: Button.X,      # X / Square
    3: Button.Y,      # Y / Triangle
    4: Button.L,      # LB / L1
    5: Button.R,      # RB / R1
    6: Button.SELECT, # Back / Select
    7: Button.START,  # Start
}

# Hat (D-pad) direction mappings
DEFAULT_HAT_MAP = {
    (0, 1): Button.DPAD_UP,
    (0, -1): Button.DPAD_DOWN,
    (-1, 0): Button.DPAD_LEFT,
    (1, 0): Button.DPAD_RIGHT,
}

MAP_FILE = os.path.expanduser('~/.config/conway/controller_map.json')


class ControllerInput:
    """Handle game controller input."""

    def __init__(self):
        """Initialize controller input."""
        pygame.joystick.init()

        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.deadzone = config.JOYSTICK_DEADZONE

        # Mapping (loaded from config or defaults)
        self.button_map = dict(DEFAULT_BUTTON_MAP)
        self.hat_map = dict(DEFAULT_HAT_MAP)
        self.hat_index = 0
        self.dpad_type = "hat"
        self.axis_map = {
            Axis.LEFT_X: 0,
            Axis.LEFT_Y: 1,
            Axis.RIGHT_X: 2,
            Axis.RIGHT_Y: 3,
        }
        self.axis_inversion = {a: False for a in Axis}

        # Load custom mapping if available
        self._load_mapping()

        # Current and previous state for edge detection
        self.state = ControllerState(
            buttons={b: False for b in Button},
            axes={a: 0.0 for a in Axis}
        )
        self.prev_state = ControllerState(
            buttons={b: False for b in Button},
            axes={a: 0.0 for a in Axis}
        )

        # Try to connect to first available controller
        self._detect_controller()

    def _load_mapping(self):
        """Load controller mapping from JSON config."""
        if not os.path.exists(MAP_FILE):
            return
        try:
            with open(MAP_FILE, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        # Build button map from saved config
        if "buttons" in data:
            self.button_map = {}
            for name, idx in data["buttons"].items():
                try:
                    self.button_map[idx] = Button[name]
                except KeyError:
                    pass

        # D-pad config
        self.dpad_type = data.get("dpad_type", "hat")
        if self.dpad_type == "hat":
            self.hat_index = data.get("hat_index", 0)

        # Axis map
        axis_lookup = {
            "LEFT_X": Axis.LEFT_X,
            "LEFT_Y": Axis.LEFT_Y,
            "RIGHT_X": Axis.RIGHT_X,
            "RIGHT_Y": Axis.RIGHT_Y,
        }
        if "axes" in data:
            for name, idx in data["axes"].items():
                if name in axis_lookup:
                    self.axis_map[axis_lookup[name]] = idx

        # Axis inversion
        if "axis_inversion" in data:
            for name, inverted in data["axis_inversion"].items():
                if name in axis_lookup:
                    self.axis_inversion[axis_lookup[name]] = inverted

    def _detect_controller(self):
        """Detect and initialize controller."""
        count = pygame.joystick.get_count()
        if count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.state.connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
        else:
            self.joystick = None
            self.state.connected = False

    def update(self):
        """Update controller state. Call once per frame."""
        # Store previous state
        self.prev_state.buttons = self.state.buttons.copy()
        self.prev_state.axes = self.state.axes.copy()

        # Check for controller connection changes
        current_count = pygame.joystick.get_count()
        if current_count > 0 and not self.state.connected:
            self._detect_controller()
        elif current_count == 0 and self.state.connected:
            self.joystick = None
            self.state.connected = False

        if not self.joystick:
            return

        # Update button states
        for button_idx, button in self.button_map.items():
            if button_idx < self.joystick.get_numbuttons():
                self.state.buttons[button] = self.joystick.get_button(button_idx)

        # Update D-pad from hat
        if self.dpad_type == "hat" and self.joystick.get_numhats() > self.hat_index:
            hat = self.joystick.get_hat(self.hat_index)
            for direction, button in self.hat_map.items():
                self.state.buttons[button] = (hat == direction)

        # Update axes
        for axis_enum, axis_idx in self.axis_map.items():
            if axis_idx < self.joystick.get_numaxes():
                value = self._apply_deadzone(self.joystick.get_axis(axis_idx))
                if self.axis_inversion.get(axis_enum, False):
                    value = -value
                self.state.axes[axis_enum] = value

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        # Scale value to start from 0 after deadzone
        sign = 1 if value > 0 else -1
        return sign * (abs(value) - self.deadzone) / (1 - self.deadzone)

    def is_pressed(self, button: Button) -> bool:
        """Check if a button is currently pressed."""
        return self.state.buttons.get(button, False)

    def just_pressed(self, button: Button) -> bool:
        """Check if a button was just pressed this frame."""
        return (self.state.buttons.get(button, False) and
                not self.prev_state.buttons.get(button, False))

    def just_released(self, button: Button) -> bool:
        """Check if a button was just released this frame."""
        return (not self.state.buttons.get(button, False) and
                self.prev_state.buttons.get(button, False))

    def get_axis(self, axis: Axis) -> float:
        """Get current axis value (-1.0 to 1.0)."""
        return self.state.axes.get(axis, 0.0)

    def get_left_stick(self):
        """Get left stick position as (x, y) tuple."""
        return (
            self.state.axes.get(Axis.LEFT_X, 0.0),
            self.state.axes.get(Axis.LEFT_Y, 0.0)
        )

    def get_right_stick(self):
        """Get right stick position as (x, y) tuple."""
        return (
            self.state.axes.get(Axis.RIGHT_X, 0.0),
            self.state.axes.get(Axis.RIGHT_Y, 0.0)
        )

    @property
    def connected(self) -> bool:
        """Check if a controller is connected."""
        return self.state.connected
