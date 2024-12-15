
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages
from .grouppn import GroupPane



class MessageLog(Log):


    def on_mount(self):
        self.clear()
        mlist = get_devicemessages()
        if mlist:
            self.write_lines(mlist)
        else:
            self.write(f"Messages from {get_devicename()} will appear here")


class MessagesPane(Container):

    def compose(self) -> ComposeResult:
        yield MessageLog(id="device-messages")

    def on_mount(self):
        self.border_title = "Device Messages"



class DeviceSc(Screen):
    """The class defining the device screen."""

    CSS_PATH = "tcss/start.tcss"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [("m", "main", "Main Screen")]


    def compose(self) -> ComposeResult:
        devicename = get_devicename()
        yield Static(devicename, id="devicename")
        yield Footer()
        yield MessagesPane(id="dev-messages-pane")
        yield GroupPane(id="dev-group-pane")

    def action_main(self) -> None:
        """Event handler called when m pressed."""
        CONNECTION = get_connection()
        CONNECTION.devicesc = None
        self.app.pop_screen()


    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
