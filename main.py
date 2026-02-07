#!/usr/bin/env python3
"""Conway's Game of Life - Main entry point."""
import pygame
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from engine.grid import Grid
from display.renderer import Renderer
from display.viewport import Viewport
from input.controller import ControllerInput
from input.keyboard import KeyboardInput
from ui.hud import HUD
from ui.editor import Editor
from states.state_machine import StateMachine
from states.boot_state import BootState
from states.menu_state import MenuState
from states.running_state import RunningState
from states.paused_state import PausedState
from states.editor_state import EditorState
from states.info_state import InfoState
from states.gallery_state import GalleryState
from states.colophon_state import ColophonState


class Game:
    """Main game class."""

    def __init__(self, fullscreen: bool = False, skip_intro: bool = False):
        """Initialize the game."""
        # Initialize pygame
        pygame.init()
        pygame.mouse.set_visible(False)

        # Create core components
        self.grid = Grid(
            config.VIRTUAL_GRID_WIDTH,
            config.VIRTUAL_GRID_HEIGHT,
            config.WRAP_MODE
        )

        self.renderer = Renderer(fullscreen=fullscreen)
        self.viewport = Viewport(
            config.VIRTUAL_GRID_WIDTH,
            config.VIRTUAL_GRID_HEIGHT
        )

        # Center viewport
        self.viewport.center_on(
            config.VIRTUAL_GRID_WIDTH // 2,
            config.VIRTUAL_GRID_HEIGHT // 2
        )

        # Input handlers
        self.controller = ControllerInput()
        self.keyboard = KeyboardInput()

        # UI components
        self.hud = HUD()
        self.editor = Editor(
            config.VIRTUAL_GRID_WIDTH,
            config.VIRTUAL_GRID_HEIGHT
        )

        # State machine
        self.state_machine = StateMachine()
        self._setup_states(skip_intro=skip_intro)

        # Game loop control
        self.running = True
        self.clock = pygame.time.Clock()
        self.target_fps = 60

    def _setup_states(self, skip_intro: bool = False):
        """Set up game states."""
        self.state_machine.add_state("boot", BootState(self))
        self.state_machine.add_state("menu", MenuState(self))
        self.state_machine.add_state("running", RunningState(self))
        self.state_machine.add_state("paused", PausedState(self))
        self.state_machine.add_state("editor", EditorState(self))
        self.state_machine.add_state("info", InfoState(self))
        self.state_machine.add_state("gallery", GalleryState(self))
        self.state_machine.add_state("colophon", ColophonState(self))

        # Start with boot screen or menu
        if skip_intro:
            self.state_machine.change_state("menu")
        else:
            self.state_machine.change_state("boot")

    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.target_fps) / 1000.0

            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.state_machine.handle_event(event)

            # Update keyboard state
            self.keyboard.update(events)

            # Update current state
            self.state_machine.update(dt)

            # Render current state
            self.state_machine.render()

        # Cleanup
        self.renderer.quit()


def main():
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Metabolic Sublimes Potluck: Game of Life")
    parser.add_argument(
        '-f', '--fullscreen',
        action='store_true',
        help='Run in fullscreen mode'
    )
    parser.add_argument(
        '-p', '--pattern',
        type=str,
        help='Load a pattern file on startup'
    )
    parser.add_argument(
        '-s', '--skip-intro',
        action='store_true',
        help='Skip the intro/boot screen'
    )

    args = parser.parse_args()

    game = Game(fullscreen=args.fullscreen, skip_intro=args.skip_intro)

    # Load pattern if specified
    if args.pattern:
        from engine.patterns import PatternLoader
        pattern = PatternLoader.load_file(args.pattern)
        if pattern:
            cx = game.grid.width // 2 - pattern.width // 2
            cy = game.grid.height // 2 - pattern.height // 2
            game.grid.load_pattern(pattern.data, cx, cy)
            game.state_machine.change_state("running")
        else:
            print(f"Warning: Could not load pattern '{args.pattern}'")

    game.run()


if __name__ == '__main__':
    main()
