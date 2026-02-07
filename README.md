# Metabolic Sublimes Potluck: Game of Life

A handheld Conway's Game of Life built with Python and Pygame, designed to run on a Raspberry Pi with a small DSI display and game controller.

Created for the [Metabolic Sublimes Study Group](https://are.na/johnnie/metabolic-sublimes-game-of-life) organized by Adriana Gallo and hosted by Index Greenpoint in NYC (Jan 17 - Feb 7, 2026).

## About

The Game of Life was created by mathematician John Conway (1937-2020) in 1970. It's a zero-player cellular automaton where complex emergent behavior arises from simple rules: cells live, die, or are born based only on their neighbors.

This version was built to demonstrate how microscopic systems on multiple levels converge to create complex behavior in large systems despite simple rules.

## Hardware

- Raspberry Pi 5 (8GB RAM)
- IPistBit 4.3" DSI LED Display
- Geekwork X1202 4-cell UPS Shield
- Game controller (mapped via built-in wizard)
- Recycled cardboard shipping box enclosure
- Custom 3D printed display stand (files in `3d_prints/`)

## Features

- **State machine architecture** - Boot sequence, menu, simulation, editor, gallery, info screens
- **Game controller support** - Full button/stick mapping with a guided configuration wizard
- **Pattern library** - 20+ built-in patterns including glider, gosper gun, copperhead, loafer, and more
- **Pattern editor** - Place, rotate, and draw patterns with controller or keyboard
- **5 color themes** - Classic, Amber, Blue, White, Matrix (cycle with `T` or L3)
- **Gallery mode** - Auto-cycles through patterns for passive display
- **Custom pixel font** - 5x7 bitmap font for retro aesthetic
- **Toroidal or bounded grids** - Configurable edge wrapping
- **4 zoom levels** - 1x, 2x, 4x, 8x with smooth viewport panning
- **Scanline and vignette effects**

## Controls

### Controller

| Button | Running | Menu | Editor |
|--------|---------|------|--------|
| A | Pause | Select | Toggle cell |
| B | Menu | Back | Back |
| X | Single step | - | Place pattern |
| Y | Editor | - | Clear pattern |
| D-pad | Step + pan | Navigate | Move cursor |
| Left stick | Pan viewport | Navigate | Move cursor |
| Right stick | Zoom | - | Zoom |
| L / R | Speed -/+ | - | Prev/next pattern |
| Start | Menu | - | Menu |
| Select | Clear grid | - | - |
| L3 | Cycle theme | Cycle theme | Cycle theme |

### Keyboard

| Key | Action |
|-----|--------|
| Space | Pause/resume |
| Arrow keys | Pan viewport |
| Page Up/Down | Zoom in/out |
| T | Cycle theme |
| E | Toggle editor |
| C | Clear grid |
| R | Randomize |
| H | Toggle HUD |
| G | Toggle grid lines |
| Escape | Menu/back |

## Setup

```bash
pip install -r requirements.txt
python main.py
```

### Options

```
python main.py -f            # Fullscreen
python main.py -s            # Skip intro
python main.py -p FILE.rle   # Load a pattern file
```

### Controller Mapping

If your controller buttons aren't mapped correctly, run the mapping wizard:

```bash
python input/controller_diagnostic.py
```

It walks through every button, stick, and d-pad input and saves the mapping to `~/.config/conway/controller_map.json`.

## Adding Patterns

Drop `.rle` or `.cells` files into the `patterns/` directory. They'll appear in the pattern browser automatically.

## Project Structure

```
main.py              Entry point
config.py            Grid, display, and controller settings
settings.py          Persistent user settings
display/             Renderer, viewport, themes, pixel font, effects
engine/              Grid simulation, pattern loading/parsing
input/               Controller and keyboard handling
states/              State machine (boot, menu, running, paused, editor, etc.)
ui/                  HUD, editor overlay, menu system
patterns/            Built-in .rle pattern files
3d_prints/           3D print files for display stand
```

## Built With

Python, Pygame, NumPy, and [Claude Code](https://claude.ai/claude-code)

## Inspiration

- LoneSoulSurfer's Game of Life Handheld
- Numberphile's 2015 interview with John Conway
- [Full list on Are.na](https://are.na/johnnie/metabolic-sublimes-game-of-life)
