
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Log, TabbedContent
from textual.screen import Screen
from textual.containers import Container

from .connections import set_devicename, get_devicename, get_devicemessages, clear_devicesc
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
        "set devicename in connections module"
        set_devicename(devicename)
        super().__init__()

    def compose(self) -> ComposeResult:
        devicename = get_devicename()
        yield Static(devicename, id="devicename")
        yield Footer()
        yield MessagesPane(id="dev-messages-pane")
        yield GroupPane(id="dev-group-pane")


    def action_main(self) -> None:
        """Event handler called when m pressed."""
        clear_devicesc()
        self.app.pop_screen()


    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
