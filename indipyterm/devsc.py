
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Log, TabbedContent
from textual.screen import Screen
from textual.containers import Container

#from .grouppn import GroupPane

from .iclient import localtimestring


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
        devicename = self.parent.parent.devicename
        messages = self.app.indiclient[devicename].messages
        if messages:
            self.write_lines( reversed([ localtimestring(t) + "  " + m for t,m in messages]) )
        else:
           self.write(f"Messages from {devicename} will appear here")


class MessagesPane(Container):

    DEFAULT_CSS = """

        MessagesPane {
            height: 6;
            background: $panel;
            border: mediumvioletred;
           }
        """


    def compose(self) -> ComposeResult:
        self.border_title = "Device Messages"
        yield MessageLog(id="device-messages")



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
        self.devicename = devicename
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(self.devicename, id="devicename")
        yield Footer()
        yield MessagesPane(id="dev-messages-pane")
        #yield GroupPane(id="dev-group-pane")


    def action_main(self) -> None:
        """Event handler called when m pressed."""
        self.app.indiclient.clientdata['devicesc'] = None
        self.app.pop_screen()


#    def action_show_tab(self, tab: str) -> None:
#        """Switch to a new tab."""
#        self.get_child_by_type(TabbedContent).active = tab
