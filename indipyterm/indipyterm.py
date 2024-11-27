
import asyncio, queue, threading

from typing import Iterable

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, VerticalScroll

from .connections import get_connection

from .startsc import StartSc
from .devicesc import DeviceSc



class IPyTerm(App):
    """An INDI terminal."""

    SCREENS = {"startsc": StartSc,
               "devicesc": DeviceSc}

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]

    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        CONNECTION = get_connection()
        self.push_screen('startsc')
        CONNECTION.app = self
        CONNECTION.startsc = self.get_screen('startsc', StartSc)
        CONNECTION.devicesc = self.get_screen("devicesc", DeviceSc)
        # Check the RXQUE every 0.1 of a second
        self.set_interval(1 / 10, CONNECTION.check_rxque)

    def action_quit(self) -> None:
        """An action to quit the program."""
        CONNECTION = get_connection()
        if CONNECTION.is_alive():
            CONNECTION.txque.put(None)
            CONNECTION.clientthread.join()
        self.exit(0)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
            )
