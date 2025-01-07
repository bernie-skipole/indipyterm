
from typing import Iterable

from textual import on
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, HorizontalScroll, VerticalScroll, Center

from .connections import get_connection, get_devicename, set_devicename, get_id, set_id, set_devicestatus, devicename_from_id

from .devicesc import DeviceSc


class DevicePane(Container):

    DEFAULT_CSS = """

            DevicePane {
                width: 100%;
                row-span: 2;
                background: $panel;
                border: dodgerblue;
                }

            DevicePane > Static {
                background: $boost;
                color: auto;
                margin-bottom: 1;
                padding: 1;
                }

             DevicePane > Button {
                width: 100%;
                }
        """

    def compose(self):
        self.border_title = "Devices"
        yield Static("No Devices found", id="no-devices")

    @on(Button.Pressed, ".devices")
    def choose_device(self, event):
        "Choose device fro the button pressed"
        devicename = devicename_from_id(event.button.id)
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

        CONNECTION.devicesc = DeviceSc(devicename)
        self.app.push_screen(CONNECTION.devicesc)


class BlobPane(HorizontalScroll):

    DEFAULT_CSS = """

        BlobPane {
            background: $panel;
            border: greenyellow;
            }
        """

    def compose(self):
        yield BlobInput(placeholder="Set a Folder to receive BLOBs", id="blob-input")

    def on_mount(self):
        self.border_title = "Set BLOB folder"
        CONNECTION = get_connection()
        if CONNECTION.blobfolderpath:
            self.border_subtitle = "Received BLOBs enabled"
        else:
            self.border_subtitle = "Received BLOBs disabled"


class MessagesPane(Container):

    DEFAULT_CSS = """

        MessagesPane {
            width: 100%;
            column-span: 2;
            background: $panel;
            border: mediumvioletred;
            }

        MessagesPane > Log {
            width: 100%;
            background: $panel;
            scrollbar-background: $panel;
            scrollbar-corner-color: $panel;
            }
        """

    def compose(self):
        self.border_title = "System Messages"
        yield Log(id="system-messages")


class ConnectionPane(Container):

    DEFAULT_CSS = """

        ConnectionPane {
            background: $panel;
            border: mediumvioletred;
            align: center middle;
            }

        ConnectionPane > Static {
            margin: 1;
            }
        """


    def compose(self):
        self.border_title = "Set INDI Server"
        CONNECTION = get_connection()
        con_input = ConInput(placeholder="Host:Port", id="con-input")
        con_status = Static("Host:Port not set", id="con-status")
        con_button = Button("Connect", id="con-button")
        if CONNECTION.host and CONNECTION.port:
            con_input.disabled = True
            con_status.update(f"Current server : {CONNECTION.host}:{CONNECTION.port}")
            con_button.label = "Disconnect"
        else:
            con_input.disabled = False
            con_status.update("Host:Port not set")
            con_button.label = "Connect"
        yield con_input
        yield con_status
        with Center():
            yield con_button


    def on_button_pressed(self, event):
        CONNECTION = get_connection()
        con_input = self.query_one("#con-input")
        con_status = self.query_one("#con-status")
        con_button = self.query_one("#con-button")

        if CONNECTION.host and CONNECTION.port:
            # call for disconnection
            CONNECTION.disconnect()
            con_input.disabled = False
            con_status.update("Host:Port not set")
            con_button.label = "Connect"
        else:
            # call for connection
            CONNECTION.connect()
            con_input.disabled = True
            con_status.update(f"Current server : {CONNECTION.host}:{CONNECTION.port}")
            con_button.label = "Disconnect"


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
            self.parent.border_subtitle = "Received BLOBs enabled"
        else:
            self.parent.border_subtitle = "Received BLOBs disabled"

    def action_submit(self):
        self.screen.focus_next('*')



class StartSc(Screen):
    """The top start screen."""

    DEFAULT_CSS = """

        StartSc > #title {
           background: $primary;
           color: $text;
           padding-left: 2;
           dock: top;
           }

        StartSc > #startsc-grid {
            height: 100%;
            min-height: 24;
            layout: grid;
            grid-size: 2 3;  /* two columns, three rows */
            grid-columns: 1fr 2fr;
            grid-rows: 2fr 1fr 1fr;
            }
        """

    ENABLE_COMMAND_PALETTE = False

    def __init__(self):
        super().__init__()

    def on_screenresume(self, event):
        "Sets status of devicescreen to 0 to indicate no devicescreen available"
        set_devicestatus(0)


    def compose(self) -> ComposeResult:
        yield Static("INDI Terminal", id="title")
        yield Footer()
        with VerticalScroll(id="startsc-grid"):
            yield DevicePane(id="device-pane")
            yield ConnectionPane(id="con-pane")
            yield BlobPane(id="blob-pane")
            yield MessagesPane(id="sys-messages-pane")
