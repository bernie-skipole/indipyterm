
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection


class DeviceSc(Screen):
    """The class defining the device screen."""

    CSS_PATH = "tcss/start.tcss"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [("m", "main", "Main Screen")]

    def compose(self) -> ComposeResult:
        yield Static("Device", id="title")
        yield Footer()

    def action_main(self) -> None:
        """Event handler called when m pressed."""
        self.app.push_screen('startsc')
