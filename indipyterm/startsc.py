
from typing import Iterable

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, HorizontalScroll, VerticalScroll, Center

from .connections import get_connection, get_devicename, set_devicename


class DevicePane(VerticalScroll):

    def on_mount(self):
        self.border_title = "Devices"

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
        set_devicename(devicename)
        devicesc = self.app.get_screen("devicesc")
        devicesc.devicename = devicename
        self.app.push_screen("devicesc")


class BlobPane(HorizontalScroll):

    def on_mount(self):
        self.border_title = "Set BLOB folder"
        CONNECTION = get_connection()
        if CONNECTION.blobfolderpath:
            self.border_subtitle = "Recieved BLOBs enabled"
        else:
            self.border_subtitle = "Recieved BLOBs disabled"


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

    def action_submit(self):
        self.screen.focus_next('*')



class BlobInput(Input):

    def on_blur(self, event):
        CONNECTION = get_connection()
        blobfolder = CONNECTION.checkblobfolder(self.value)
        self.clear()
        self.insert_text_at_cursor(blobfolder)
        if CONNECTION.blobfolderpath:
            self.parent.border_subtitle = "Recieved BLOBs enabled"
        else:
            self.parent.border_subtitle = "Recieved BLOBs disabled"

    def action_submit(self):
        self.screen.focus_next('*')




class StartSc(Screen):
    """The top start screen."""

    CSS_PATH = "tcss/start.tcss"

    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield Static("INDI Terminal", id="title")
        yield Footer()
        with Container(id="startsc-grid"):
            with DevicePane(id="device-pane"):
                yield Static("No Devices found", id="no-devices")
            with ConnectionPane(id="con-pane"):
                yield ConInput(placeholder="Host:Port", id="con-input")
                yield Static("Host:Port not set", id="con-status")
                with Center():
                    yield Button("Connect", id="con-button")
            with BlobPane(id="blob-pane"):
                yield BlobInput(placeholder="Set a Folder to receive BLOBs", id="blob-input")
            with MessagesPane(id="sys-messages-pane"):
                yield Log(id="system-messages")
