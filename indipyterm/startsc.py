
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection


class DevicePane(VerticalScroll):

    def on_mount(self):
        self.border_title = "Devices"



class MessagesPane(VerticalScroll):

    def on_mount(self):
        self.border_title = "System Messages"


class ConnectionPane(VerticalScroll):

    def on_mount(self):
        self.border_title = "Set INDI Server"
        CONNECTION = get_connection()
        con_input = self.query_one("#con-input")
        con_status = self.query_one("#con-status")
        con_button = self.query_one("#con-button")
        if CONNECTION.host and CONNECTION.port:
            con_input.disabled = True
            con_status.update(f"Current server : {CONNECTION.host}:{CONNECTION.port}")
            con_button.label = "Disconnect"
        else:
            con_input.disabled = False
            con_status.update("Host:Port not set")
            con_button.label = "Connect"

    def on_button_pressed(self, event):
        CONNECTION = get_connection()
        if CONNECTION.host and CONNECTION.port:
            # call for disconnection
            CONNECTION.disconnect()
        else:
            # call for connection
            CONNECTION.connect()
        # and set up button labels
        self.on_mount()



class ConInput(Input):

    def on_blur(self, event):
        CONNECTION = get_connection()
        hostport = CONNECTION.checkhostport(self.value)
        self.clear()
        self.insert_text_at_cursor(hostport)

    def on_submitted(self, event):
        CONNECTION = get_connection()
        hostport = CONNECTION.checkhostport(self.value)
        self.clear()
        self.insert_text_at_cursor(hostport)




class StartSc(Screen):
    """The top start screen."""

    CSS_PATH = "tcss/start.tcss"

    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield Static("INDI Terminal", id="title")
        yield Footer()
        with Container(id="startsc-grid"):
            with DevicePane(id="left-pane"):
                yield Static("No Devices found", id="no-devices")
            with ConnectionPane(id="top-right"):
                yield ConInput(placeholder="Host:Port", id="con-input")
                yield Static("Host:Port not set", id="con-status")
                with Center():
                    yield Button("Connect", id="con-button")
            with Container(id="bottom-right"):
                yield Static("This")
                yield Static("panel")
                yield Static("is")
                yield Static("using")
                yield Static("grid layout!", id="bottom-right-final")
            with MessagesPane(id="bottom"):
                yield Log(id="system-messages")
