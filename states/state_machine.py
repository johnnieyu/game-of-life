"""State machine for game state management."""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class State(ABC):
    """Base class for game states."""

    def __init__(self, game):
        """
        Initialize state.

        Args:
            game: Reference to main game instance
        """
        self.game = game

    @property
    @abstractmethod
    def name(self) -> str:
        """State name for display."""
        pass

    def enter(self, prev_state: Optional['State'] = None):
        """Called when entering this state."""
        pass

    def exit(self, next_state: Optional['State'] = None):
        """Called when exiting this state."""
        pass

    @abstractmethod
    def update(self, dt: float):
        """
        Update state logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    @abstractmethod
    def render(self):
        """Render state visuals."""
        pass

    def handle_event(self, event) -> Optional[str]:
        """
        Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            Next state name if state should change, None otherwise
        """
        return None


class StateMachine:
    """Manages game states and transitions."""

    def __init__(self):
        """Initialize state machine."""
        self.states: Dict[str, State] = {}
        self.current_state: Optional[State] = None
        self.previous_state: Optional[State] = None

    def add_state(self, name: str, state: State):
        """Add a state to the machine."""
        self.states[name] = state

    def change_state(self, name: str):
        """
        Change to a different state.

        Args:
            name: Name of state to change to
        """
        if name not in self.states:
            print(f"Warning: Unknown state '{name}'")
            return

        next_state = self.states[name]

        if self.current_state:
            self.current_state.exit(next_state)

        self.previous_state = self.current_state
        self.current_state = next_state
        self.current_state.enter(self.previous_state)

    def update(self, dt: float):
        """Update current state."""
        if self.current_state:
            self.current_state.update(dt)

    def render(self):
        """Render current state."""
        if self.current_state:
            self.current_state.render()

    def handle_event(self, event):
        """Pass event to current state."""
        if self.current_state:
            next_state = self.current_state.handle_event(event)
            if next_state:
                self.change_state(next_state)

    @property
    def state_name(self) -> str:
        """Get current state name."""
        if self.current_state:
            return self.current_state.name
        return ""
