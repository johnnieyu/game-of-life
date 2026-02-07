"""Pattern loading and parsing for Game of Life."""
import numpy as np
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Pattern:
    """Represents a Game of Life pattern."""
    name: str
    data: np.ndarray
    width: int
    height: int
    author: str = ""
    description: str = ""
    filename: str = ""

    @property
    def population(self) -> int:
        return int(np.sum(self.data))


class PatternLoader:
    """Load and parse Game of Life patterns."""

    # Built-in patterns defined in code
    BUILTIN_PATTERNS = {
        # Still lifes
        'block': {
            'data': [[1, 1], [1, 1]],
            'description': 'Smallest still life'
        },
        'beehive': {
            'data': [[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]],
            'description': '6-cell still life'
        },
        'loaf': {
            'data': [[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]],
            'description': '7-cell still life'
        },
        'boat': {
            'data': [[1, 1, 0], [1, 0, 1], [0, 1, 0]],
            'description': '5-cell still life'
        },
        'tub': {
            'data': [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
            'description': '4-cell still life'
        },

        # Oscillators
        'blinker': {
            'data': [[1, 1, 1]],
            'description': 'Period 2 oscillator'
        },
        'toad': {
            'data': [[0, 1, 1, 1], [1, 1, 1, 0]],
            'description': 'Period 2 oscillator'
        },
        'beacon': {
            'data': [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]],
            'description': 'Period 2 oscillator'
        },
        'pulsar': {
            'data': [
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            ],
            'description': 'Period 3 oscillator'
        },
        'pentadecathlon': {
            'data': [
                [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
                [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            ],
            'description': 'Period 15 oscillator'
        },

        # Spaceships
        'glider': {
            'data': [[0, 1, 0], [0, 0, 1], [1, 1, 1]],
            'description': 'Smallest spaceship'
        },
        'lwss': {
            'data': [
                [1, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [0, 1, 1, 1, 1],
            ],
            'description': 'Lightweight spaceship'
        },
        'mwss': {
            'data': [
                [0, 0, 1, 0, 0, 0],
                [1, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1],
                [0, 1, 1, 1, 1, 1],
            ],
            'description': 'Middleweight spaceship'
        },
        'hwss': {
            'data': [
                [0, 0, 1, 1, 0, 0, 0],
                [1, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [0, 1, 1, 1, 1, 1, 1],
            ],
            'description': 'Heavyweight spaceship'
        },

        # Guns
        'gosper_glider_gun': {
            'data': [
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            ],
            'description': 'First known gun pattern'
        },

        # Methuselahs
        'r_pentomino': {
            'data': [[0, 1, 1], [1, 1, 0], [0, 1, 0]],
            'description': 'Methuselah - stabilizes at gen 1103'
        },
        'diehard': {
            'data': [[0, 0, 0, 0, 0, 0, 1, 0], [1, 1, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1, 1, 1]],
            'description': 'Methuselah - dies at gen 130'
        },
        'acorn': {
            'data': [[0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0], [1, 1, 0, 0, 1, 1, 1]],
            'description': 'Methuselah - stabilizes at gen 5206'
        },

        # Other interesting patterns
        'infinite_1': {
            'data': [
                [1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1],
                [0, 1, 1, 0, 1],
                [1, 0, 1, 0, 1],
            ],
            'description': 'Infinite growth pattern'
        },
    }

    @classmethod
    def get_builtin(cls, name: str) -> Optional[Pattern]:
        """Get a built-in pattern by name."""
        if name not in cls.BUILTIN_PATTERNS:
            return None

        info = cls.BUILTIN_PATTERNS[name]
        data = np.array(info['data'], dtype=np.uint8)

        return Pattern(
            name=name,
            data=data,
            width=data.shape[1],
            height=data.shape[0],
            description=info.get('description', '')
        )

    @classmethod
    def list_builtin(cls) -> List[str]:
        """List all built-in pattern names."""
        return list(cls.BUILTIN_PATTERNS.keys())

    @classmethod
    def parse_rle(cls, content: str) -> Tuple[np.ndarray, Dict]:
        """
        Parse RLE (Run Length Encoded) pattern format.

        Returns:
            Tuple of (pattern data, metadata dict)
        """
        lines = content.strip().split('\n')

        metadata = {'name': '', 'author': '', 'description': ''}
        width = height = 0
        pattern_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Comment lines
            if line.startswith('#'):
                if line.startswith('#N'):
                    metadata['name'] = line[2:].strip()
                elif line.startswith('#O'):
                    metadata['author'] = line[2:].strip()
                elif line.startswith('#C') or line.startswith('#c'):
                    desc = line[2:].strip()
                    if metadata['description']:
                        metadata['description'] += ' ' + desc
                    else:
                        metadata['description'] = desc
                continue

            # Header line: x = N, y = M
            if line.startswith('x'):
                match = re.search(r'x\s*=\s*(\d+).*y\s*=\s*(\d+)', line)
                if match:
                    width = int(match.group(1))
                    height = int(match.group(2))
                continue

            # Pattern data
            pattern_lines.append(line)

        # Join pattern lines and parse
        pattern_str = ''.join(pattern_lines)

        # Initialize grid
        if width == 0 or height == 0:
            # Try to determine from pattern
            width = height = 100  # Default max

        data = np.zeros((height, width), dtype=np.uint8)

        x, y = 0, 0
        run_count = ''

        for char in pattern_str:
            if char.isdigit():
                run_count += char
            elif char == 'b':  # Dead cell
                count = int(run_count) if run_count else 1
                x += count
                run_count = ''
            elif char == 'o':  # Alive cell
                count = int(run_count) if run_count else 1
                for _ in range(count):
                    if y < height and x < width:
                        data[y, x] = 1
                    x += 1
                run_count = ''
            elif char == '$':  # End of row
                count = int(run_count) if run_count else 1
                y += count
                x = 0
                run_count = ''
            elif char == '!':  # End of pattern
                break

        # Trim to actual size
        rows = np.any(data, axis=1)
        cols = np.any(data, axis=0)
        if np.any(rows) and np.any(cols):
            y_min, y_max = np.where(rows)[0][[0, -1]]
            x_min, x_max = np.where(cols)[0][[0, -1]]
            data = data[y_min:y_max+1, x_min:x_max+1]

        return data, metadata

    @classmethod
    def parse_cells(cls, content: str) -> Tuple[np.ndarray, Dict]:
        """
        Parse plaintext .cells format.

        Returns:
            Tuple of (pattern data, metadata dict)
        """
        lines = content.strip().split('\n')

        metadata = {'name': '', 'author': '', 'description': ''}
        pattern_lines = []

        for line in lines:
            if line.startswith('!'):
                # Comment/metadata
                text = line[1:].strip()
                if text.lower().startswith('name:'):
                    metadata['name'] = text[5:].strip()
                elif text.lower().startswith('author:'):
                    metadata['author'] = text[7:].strip()
                else:
                    if metadata['description']:
                        metadata['description'] += ' ' + text
                    else:
                        metadata['description'] = text
            elif line.strip():
                pattern_lines.append(line.rstrip())

        if not pattern_lines:
            return np.zeros((1, 1), dtype=np.uint8), metadata

        # Determine dimensions
        height = len(pattern_lines)
        width = max(len(line) for line in pattern_lines)

        data = np.zeros((height, width), dtype=np.uint8)

        for y, line in enumerate(pattern_lines):
            for x, char in enumerate(line):
                if char in 'O*':  # Alive markers
                    data[y, x] = 1

        return data, metadata

    @classmethod
    def load_file(cls, filepath: str) -> Optional[Pattern]:
        """Load a pattern from a file."""
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r') as f:
            content = f.read()

        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.rle':
            data, metadata = cls.parse_rle(content)
        elif ext == '.cells':
            data, metadata = cls.parse_cells(content)
        else:
            return None

        name = metadata.get('name') or os.path.splitext(os.path.basename(filepath))[0]

        return Pattern(
            name=name,
            data=data,
            width=data.shape[1],
            height=data.shape[0],
            author=metadata.get('author', ''),
            description=metadata.get('description', ''),
            filename=filepath
        )

    @classmethod
    def load_directory(cls, directory: str) -> List[Pattern]:
        """Load all patterns from a directory."""
        patterns = []

        if not os.path.isdir(directory):
            return patterns

        for filename in sorted(os.listdir(directory)):
            if filename.endswith(('.rle', '.cells')):
                filepath = os.path.join(directory, filename)
                pattern = cls.load_file(filepath)
                if pattern:
                    patterns.append(pattern)

        return patterns
