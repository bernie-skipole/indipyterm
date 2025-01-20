
import pathlib

from textual.app import App
from textual import on
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Button, Log, Input
from textual.screen import Screen
from textual.containers import Container, HorizontalScroll, VerticalScroll, Center
from textual.message import Message

from .iclient import ItemID, IClient, localtimestring


#from .devicesc import DeviceSc



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

    class NewButton(Message):
        """Add a new button."""

        def __init__(self, devicename: str) -> None:
            self.devicename = devicename
            super().__init__()

    class ClearDevices(Message):
        pass

    class DelButton(Message):
        """Delete a button."""

        def __init__(self, deviceid: str) -> None:
            self.deviceid = deviceid
            super().__init__()

    def compose(self):
        self.border_title = "Devices"
        devices = self.app.indiclient.enabledlen()
        # The number of enabled devices
        if not devices:
            yield Static("No Devices found", id="no-devices")
        else:
            for devicename in self.app.indiclient:
                deviceid = self.app.itemid.set_devicid(devicename)
                yield Button(devicename, variant="primary", classes="devices", id=deviceid)


    def on_device_pane_new_button(self, message: NewButton) -> None:
        devicename = message.devicename
        deviceid = self.app.itemid.set_devicid(devicename)
        self.remove_children("#no-devices")
        self.mount(Button(devicename, variant="primary", classes="devices", id=deviceid))

    def on_device_pane_clear_devices(self, message: ClearDevices) -> None:
        if self.query(".devices"):
            self.remove_children(".devices")
            self.mount(Static("No Devices found", id="no-devices"))

    def on_device_pane_del_button(self, message: DelButton) -> None:
        deviceid = message.deviceid
        self.remove_children(f"#{deviceid}")


#    @on(Button.Pressed, ".devices")
#    def choose_device(self, event):
#        "Choose device from the button pressed"
#        devicename = devicename_from_id(event.button.id)
#        if not devicename:
#            return
#        CONNECTION = get_connection()
#        if not CONNECTION.snapshot:
#            return
#        if devicename not in CONNECTION.snapshot:
#            # An unknown device
#            return
#        if not CONNECTION.snapshot[devicename].enable:
#            # This device is disabled
#            return

#        CONNECTION.devicesc = DeviceSc(devicename)
#        self.app.push_screen(CONNECTION.devicesc)


class BlobPane(HorizontalScroll):

    DEFAULT_CSS = """

        BlobPane {
            background: $panel;
            border: greenyellow;
            }
        """

    def compose(self):
        self.border_title = "Set BLOB folder"
        yield BlobInput(placeholder="Set a Folder to receive BLOBs", id="blob-input")

    def on_mount(self):
        iclient = self.app.indiclient
        if iclient is None:
            self.border_subtitle = "Received BLOBs disabled"
            return
        if iclient.BLOBfolder:
            self.border_subtitle = "Received BLOBs enabled"
        else:
            self.border_subtitle = "Received BLOBs disabled"


class BlobInput(Input):

    def on_mount(self):
        if self.app.blobfolder:
            self.insert_text_at_cursor(str(self.app.blobfolder))

    def on_blur(self, event):
        iclient = self.app.indiclient
        if not self.value:
            self.app.blobfolder = None
            if iclient:
                iclient.BLOBfolder = None
            self.clear()
            self.insert_text_at_cursor('')
            self.parent.border_subtitle = "Received BLOBs disabled"
            return

        blobfolder = pathlib.Path(self.value).expanduser().resolve()
        if not blobfolder.is_dir():
            self.app.blobfolder = None
            if iclient:
                iclient.BLOBfolder = None
            self.clear()
            self.insert_text_at_cursor('Invalid Folder')
            self.parent.border_subtitle = "Received BLOBs disabled"
            return

        self.app.blobfolder = blobfolder
        if iclient:
            iclient.BLOBfolder = blobfolder
        self.clear()
        self.insert_text_at_cursor(str(blobfolder))
        self.parent.border_subtitle = "Received BLOBs enabled"


    def action_submit(self):
        self.screen.focus_next('*')



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

    class ShowLogs(Message):
        """pass messages to the pane."""

        def __init__(self, messagelog: str) -> None:
            self.messagelog = messagelog
            super().__init__()

    def compose(self):
        self.border_title = "System Messages"
        yield Log(id="system-messages")

    def on_messages_pane_show_logs(self, message: ShowLogs) -> None:
        log = self.query_one("#system-messages")
        if log.line_count < 32:
            log.write_line(message.messagelog)
            return
        # if greater than 32, clear logs, and show the last eight
        # stored as a deque in indiclient
        log.clear()
        messages = list(self.app.indiclient.messages)
        mlist = reversed([ localtimestring(t) + "  " + m for t,m in messages ])
        log.write_lines(mlist)



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
        con_input = ConInput(placeholder="Host:Port", id="con-input")
        con_status = Static("Host:Port not set", id="con-status")
        con_button = Button("Connect", id="con-button")
        if self.app.indihost and self.app.indiport:
            con_input.disabled = True
            con_status.update(f"Current server : {self.app.indihost}:{self.app.indiport}")
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
        con_input = self.query_one("#con-input")
        con_status = self.query_one("#con-status")
        con_button = self.query_one("#con-button")

        if self.app.indihost and self.app.indiport:
            # call for disconnection
#            CONNECTION.disconnect()
            con_input.disabled = False
            con_status.update("Host:Port not set")
            con_button.label = "Connect"
        else:
            # call for connection
            self.app.indiclient = IClient(indihost=self.app.indihost, indiport=self.app.indiport, app=self.app)
            if self.app.blobfolder:
                self.app.indiclient.BLOBfolder = self.app.blobfolder
            con_input.disabled = True
            con_status.update(f"Current server : {self.app.indihost}:{self.app.indiport}")
            con_button.label = "Disconnect"


class ConInput(Input):

    def on_blur(self, event):

        hostport = self.value.strip()
        if hostport:
            hostportlist = hostport.split(":")
            if len(hostportlist) == 2:
                host = hostportlist[0].strip()
                port = hostportlist[1].strip()
                if not host:
                    host = "localhost"
                if not port.isdigit():
                    port = "7624"
                hostport = f"{host}:{port}"
            else:
                host = hostportlist[0].strip()
                if host:
                    hostport = host +":7624"
                else:
                    hostport = "localhost:7624"
        else:
            hostport = "localhost:7624"
        self.clear()
        self.insert_text_at_cursor(hostport)

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


    def compose(self) -> ComposeResult:
        yield Static("INDI Terminal", id="title")
        yield Footer()
        with VerticalScroll(id="startsc-grid"):
            yield DevicePane(id="device-pane")
            yield ConnectionPane(id="con-pane")
            yield BlobPane(id="blob-pane")
            yield MessagesPane(id="sys-messages-pane")


class IPyTerm(App):
    """An INDI terminal."""

    SCREENS = {"startsc": StartSc}

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]

    ENABLE_COMMAND_PALETTE = False

    def __init__(self, host="localhost", port=7624, blobfolder=None):
        self.indihost = host
        self.indiport = port
        if blobfolder:
            bf = pathlib.Path(blobfolder).expanduser().resolve()
            if bf.is_dir():
                self.blobfolder = bf
            else:
                self.blobfolder = None
        else:
            self.blobfolder = None
        self.itemid = ItemID()
        self.indiclient = IClient(indihost=host, indiport=port, app=self)
        if self.blobfolder:
            self.indiclient.BLOBfolder = self.blobfolder
        super().__init__()


    def on_mount(self) -> None:
        """Start the worker which runs self.indiclient.asyncrun()
           and show the start screen"""
        self.run_worker(self.indiclient.asyncrun(), exclusive=True)
        self.push_screen('startsc')


    async def action_quit(self) -> None:
        """An action to quit the program."""
        if self.indiclient:
            self.indiclient.shutdown()
            # and wait for it to shutdown
            await self.indiclient.stopped.wait()
        self.exit(0)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
            )
