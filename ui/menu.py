"""Menu system for Game of Life."""
import pygame
from typing import List, Optional, Callable, Any
from dataclasses import dataclass, field
from display.renderer import Renderer


@dataclass
class MenuItem:
    """A single menu item."""
    label: str
    action: Optional[Callable] = None
    description: str = ""
    value: Any = None
    submenu: Optional['Menu'] = None


class Menu:
    """Menu navigation and rendering."""

    def __init__(self, title: str, items: List[MenuItem]):
        """
        Initialize menu.

        Args:
            title: Menu title
            items: List of menu items
        """
        self.title = title
        self.items = items
        self.selected_index = 0
        self.visible = False
        self.parent: Optional[Menu] = None

    def show(self):
        """Show the menu."""
        self.visible = True
        self.selected_index = 0

    def hide(self):
        """Hide the menu."""
        self.visible = False

    def navigate_up(self):
        """Move selection up."""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)

    def navigate_down(self):
        """Move selection down."""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)

    def select(self) -> Optional[Any]:
        """
        Select current item.

        Returns:
            Result of item action, or submenu if present
        """
        if not self.items:
            return None

        item = self.items[self.selected_index]

        if item.submenu:
            item.submenu.parent = self
            return item.submenu

        if item.action:
            return item.action()

        return item.value

    def back(self) -> Optional['Menu']:
        """
        Go back to parent menu.

        Returns:
            Parent menu if exists
        """
        return self.parent

    @property
    def selected_item(self) -> Optional[MenuItem]:
        """Get currently selected item."""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def render(self, renderer: Renderer, x: int = None, y: int = None):
        """Render the menu."""
        if not self.visible:
            return

        screen_w = renderer.screen_width
        screen_h = renderer.screen_height

        # Calculate menu dimensions
        item_height = 40
        padding = 20
        menu_height = len(self.items) * item_height + padding * 3 + 50  # +50 for title
        menu_width = 400

        # Center menu if no position given
        if x is None:
            x = (screen_w - menu_width) // 2
        if y is None:
            y = (screen_h - menu_height) // 2

        # Draw background
        renderer.render_box(x, y, menu_width, menu_height, alpha=230)

        # Draw title
        renderer.render_text(
            self.title,
            x + menu_width // 2,
            y + padding + 15,
            size='large',
            center=True
        )

        # Draw items
        item_y = y + padding * 2 + 50

        for i, item in enumerate(self.items):
            is_selected = i == self.selected_index

            # Draw highlight for selected item
            if is_selected:
                renderer.render_box(
                    x + 10,
                    item_y - 5,
                    menu_width - 20,
                    item_height - 5,
                    renderer.theme.menu_highlight,
                    alpha=200
                )

            # Draw item text
            color = renderer.theme.text_highlight if is_selected else renderer.theme.text
            renderer.render_text(
                item.label,
                x + padding,
                item_y,
                size='medium',
                color=color
            )

            item_y += item_height

        # Draw description for selected item
        if self.selected_item and self.selected_item.description:
            renderer.render_text(
                self.selected_item.description,
                x + menu_width // 2,
                y + menu_height - padding,
                size='small',
                center=True
            )


class PatternBrowser(Menu):
    """Pattern selection menu with preview."""

    def __init__(self, patterns: List, on_select: Callable):
        """
        Initialize pattern browser.

        Args:
            patterns: List of Pattern objects
            on_select: Callback when pattern is selected
        """
        items = [
            MenuItem(
                label=p.name,
                description=p.description,
                value=p,
                action=lambda pat=p: on_select(pat)
            )
            for p in patterns
        ]
        super().__init__("Select Pattern", items)
        self.patterns = patterns
        self.on_select = on_select

    def render(self, renderer: Renderer, x: int = None, y: int = None):
        """Render pattern browser with preview."""
        super().render(renderer, x, y)

        if not self.visible or not self.patterns:
            return

        # Draw pattern preview
        pattern = self.patterns[self.selected_index]

        screen_w = renderer.screen_width
        preview_x = screen_w - 200
        preview_y = 100

        # Preview box
        renderer.render_box(preview_x - 10, preview_y - 10, 180, 180, alpha=200)

        # Draw pattern preview (scaled to fit)
        data = pattern.data
        h, w = data.shape

        # Calculate scale to fit in 160x160 box
        scale = min(160 // max(w, 1), 160 // max(h, 1), 8)
        scale = max(1, scale)

        offset_x = preview_x + (160 - w * scale) // 2
        offset_y = preview_y + (160 - h * scale) // 2

        for row in range(h):
            for col in range(w):
                if data[row, col]:
                    pygame.draw.rect(
                        renderer.screen,
                        renderer.theme.cell_alive,
                        (offset_x + col * scale,
                         offset_y + row * scale,
                         scale, scale)
                    )

        # Pattern info
        renderer.render_text(
            f"{w}x{h}",
            preview_x + 80,
            preview_y + 170,
            size='small',
            center=True
        )
