
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Log, TabbedContent, TabPane
from textual.screen import Screen
from textual.containers import Container, VerticalScroll

from .iclient import localtimestring



class GroupTabPane(TabPane):

    def __init__(self, groupname, groupid):
        self.groupname = groupname

        super().__init__(groupname, id=groupid)

    def compose(self):
        "For every vector draw it"
        devicename = self.app.itemid.devicename
        device = self.app.indiclient[devicename]
        vectors = list(vector for vector in device.values() if vector.group == self.groupname and vector.enable)
        with VerticalScroll():
            for vector in vectors:
                #yield VectorPane(vector)
                yield Static(vector.name)

    def add_vector(self, vector):
        "Add a vector to this tab"
        # get the VerticalScroll
        vs = self.query_one(VerticalScroll)
        #vs.mount(VectorPane(vector))
        vs.mount(Static(vector.name))



class GroupPane(Container):

    DEFAULT_CSS = """

        GroupPane {
            width: 100%;
            padding: 1;
            min-height: 10;
            }
        """

    def compose(self):

        devicename = self.app.itemid.devicename
        device = self.app.indiclient[devicename]
        groupset = set(vector.group for vector in device.values() if vector.enable)
        grouplist = list(groupset)
        grouplist.sort()
        with TabbedContent(id="dev_groups"):
            for groupname in grouplist:
                groupid = self.app.itemid.set_group_id(groupname)
                yield GroupTabPane(groupname, groupid)

    def add_group(self, groupname):
        tc = self.query_one('#dev_groups')
        groupid = self.app.itemid.set_group_id(groupname)
        tc.add_pane(GroupTabPane(groupname, groupid))



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
        devicename = self.app.itemid.devicename
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
        self.app.itemid.devicename = devicename
        super().__init__()

    def compose(self) -> ComposeResult:
        devicename = self.app.itemid.devicename
        yield Static(devicename, id="devicename")
        yield Footer()
        yield MessagesPane(id="dev-messages-pane")
        yield GroupPane(id="dev-group-pane")


    def action_main(self) -> None:
        """Event handler called when m pressed."""
        self.app.indiclient.clientdata['devicesc'] = None
        self.app.pop_screen()


    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
