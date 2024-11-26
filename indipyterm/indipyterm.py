
import asyncio, queue, threading

from typing import Iterable

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll

from .connections import get_connection

from .startsc import StartSc
from .devicesc import DeviceSc



class IPyTerm(App):
    """An INDI terminal."""

    SCREENS = {"startsc": StartSc}

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]

    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        CONNECTION = get_connection()
        self.push_screen('startsc')
        CONNECTION.startsc = self.query_one(StartSc)
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


    @on(Button.Pressed, ".devices")
    def choose_device(self, event):
        "Each device button has name devicename"
        devicename = event.button.name
        if not devicename:
            return
        CONNECTION = get_connection()
        if not CONNECTION.snapshot:
            return
        if devicename not in CONNECTION.snapshot:
            # An unknown device
            return
        if not CONNECTION.snapshot[devicename].enable:
            # This device is disabled
            return
        if devicename not in CONNECTION.screens:
            devicescreen = DeviceSc()
            self.install_screen(devicescreen, name=devicename)
            CONNECTION.screens[devicename] = devicescreen
        self.push_screen(devicename)
