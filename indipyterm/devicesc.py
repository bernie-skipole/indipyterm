
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages
from .grouppn import GroupPane


class DevHead(Static):

    devicename = reactive(get_devicename)

    def watch_devicename(self, devicename:str) -> None:
        self.update(devicename)


class MessageLog(Log):

    devicename = reactive(get_devicename)

    def watch_devicename(self, devicename:str) -> None:
        self.clear()
        mlist = get_devicemessages(devicename)
        if mlist:
            self.write_lines(mlist)
        else:
            self.write(f"Messages from {devicename} will appear here")


class MessagesPane(VerticalScroll):

    devicename = reactive(get_devicename)

    def compose(self) -> ComposeResult:
        yield MessageLog(id="device-messages").data_bind(MessagesPane.devicename)

    def on_mount(self):
        self.border_title = "Device Messages"



class DeviceSc(Screen):
    """The class defining the device screen."""

    CSS_PATH = "tcss/start.tcss"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [("m", "main", "Main Screen")]

    devicename = reactive(get_devicename)

    def compose(self) -> ComposeResult:
        yield DevHead(id="devicename").data_bind(DeviceSc.devicename)
        yield Footer()
        yield MessagesPane(id="dev-messages-pane").data_bind(DeviceSc.devicename)
        yield GroupPane(id="dev-group-pane").data_bind(DeviceSc.devicename)


    def action_main(self) -> None:
        """Event handler called when m pressed."""
        self.app.push_screen('startsc')

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
