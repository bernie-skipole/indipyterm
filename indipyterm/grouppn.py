
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages





class GroupPane(VerticalScroll):

    devicename = reactive(get_devicename)

    def on_mount(self):
        self.border_title = "Device Group"

    def compose(self):
        with TabbedContent():
            with TabPane("HELLO"):
                yield Static("HELLO")  # First tab
            with TabPane("GOODBYE"):
                yield Static("GOODBYE")
