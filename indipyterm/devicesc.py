
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, set_devicename, get_devicename, get_devicemessages, set_devicestatus
from .grouppn import GroupPane



class MessageLog(Log):

    DEFAULT_CSS = """

        MessageLog {
            width: 100%;
            height: 100%;
            background: $panel;
            scrollbar-background: $panel;
            scrollbar-corner-color: $panel;
            }
        """

    def on_mount(self):
        self.clear()
        mlist = get_devicemessages()
        if mlist:
            self.write_lines(mlist)
        else:
            self.write(f"Messages from {get_devicename()} will appear here")


class MessagesPane(Container):

    DEFAULT_CSS = """

        MessagesPane {
            height: 6;
            background: $panel;
            border: mediumvioletred;
           }
        """


    def compose(self) -> ComposeResult:
        yield MessageLog(id="device-messages")

    def on_mount(self):
        self.border_title = "Device Messages"



class DeviceSc(Screen):
    """The class defining the device screen."""

    DEFAULT_CSS = """

        DeviceSc >#devicename {
           height: 1;
           background: $primary;
           color: $text;
           padding-left: 2;
           dock: top;
           }
        """

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [("m", "main", "Main Screen")]

    def __init__(self, devicename):
        "set devicestatus to 1 to indicate screen loading"
        set_devicestatus(1)
        set_devicename(devicename)
        super().__init__()

    def compose(self) -> ComposeResult:
        devicename = get_devicename()
        yield Static(devicename, id="devicename")
        yield Footer()
        yield MessagesPane(id="dev-messages-pane")
        yield GroupPane(id="dev-group-pane")

    def on_mount(self, event) -> None:
        "Indicate this devicesscreen is loaded"
        set_devicestatus(2)

    def action_main(self) -> None:
        """Event handler called when m pressed."""
        set_devicestatus(0)
        self.app.pop_screen()


    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
