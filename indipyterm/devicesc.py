
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection


class MessagesPane(VerticalScroll):

    def on_mount(self):
        self.border_title = "Device Messages"


class DeviceSc(Screen):
    """The class defining the device screen."""

    CSS_PATH = "tcss/start.tcss"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [("m", "main", "Main Screen")]

    def compose(self) -> ComposeResult:
        CONNECTION = get_connection()
        yield Static(CONNECTION.devicename, id="title")
        yield Footer()
        with Container():
            with MessagesPane(id="dev-messages-pane"):
                yield Log(id="device-messages")


    def action_main(self) -> None:
        """Event handler called when m pressed."""
        CONNECTION = get_connection()
        CONNECTION.devicename = None
        self.app.push_screen('startsc')
