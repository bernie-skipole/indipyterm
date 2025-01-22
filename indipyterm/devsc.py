
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Log, TabbedContent, TabPane
from textual.screen import Screen
from textual.containers import Container, VerticalScroll

#from .grouppn import GroupPane

from .iclient import localtimestring



class GroupTabPane(TabPane):

    def __init__(self, tabtitle, groupname):
        self.groupname = groupname
        super().__init__(tabtitle, id=set_group_id(groupname))

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        devicename = get_devicename()
        vectors = list(vector for vector in snapshot[devicename].values() if vector.group == self.groupname and vector.enable)
        with VerticalScroll():
            for vector in vectors:
                yield VectorPane(vector)

    def add_vector(self, vector):
        "Add a vector to this tab"
        # get the VerticalScroll
        vs = self.query_one(VerticalScroll)
        vs.mount(VectorPane(vector))



class GroupPane(Container):

    DEFAULT_CSS = """

        GroupPane {
            width: 100%;
            padding: 1;
            min-height: 10;
            }
        """

    def compose(self):
        grouplist = get_devicegroups()
        with TabbedContent(id="dev_groups"):
            for groupname in grouplist:
                yield GroupTabPane(groupname, groupname=groupname)

    def add_group(self, groupname):
        tc = self.query_one('#dev_groups')
        tc.add_pane(GroupTabPane(groupname, groupname=groupname))



########
def get_devicegroups(devicename=None):
    "Returns a list of groups for the device"
    if devicename is None:
        devicename = get_devicename()
    if not devicename:
        return
    connection = get_connection()
    snapshot = connection.snapshot
    if not snapshot:
        return
    if devicename not in snapshot:
        return
    device = snapshot[devicename]
    groupset = set(vector.group for vector in device.values() if vector.enable)
    if not groupset:
        return
    grouplist = list(groupset)
    grouplist.sort()
    return grouplist
##############






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
        yield GroupPane(id="dev-group-pane")


    def action_main(self) -> None:
        """Event handler called when m pressed."""
        self.app.indiclient.clientdata['devicesc'] = None
        self.app.pop_screen()


    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
