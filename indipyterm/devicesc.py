
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Log, TabbedContent, TabPane
from textual.screen import Screen
from textual.containers import Container, VerticalScroll
from textual.message import Message

from .iclient import localtimestring

from .vectorpn import VectorPane


class GroupTabPane(TabPane):

    class AddVector(Message):
        """pass new vector to the pane."""

        def __init__(self, vector):
            self.vector = vector
            super().__init__()

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
                yield VectorPane(vector)

    def on_group_tab_pane_add_vector(self, message: AddVector) -> None:
        "Add a vector to this tab"
        vector = message.vector
        # get the VerticalScroll containing the vectors
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


    class AddGroup(Message):
        """pass new group to the pane."""

        def __init__(self, groupname: str) -> None:
            self.groupname = groupname
            super().__init__()


    class DelVector(Message):
        "Delete this vector"

        def __init__(self, vector, vectorid):
            self.vector = vector
            self.vectorid = vectorid
            super().__init__()


    def compose(self):
        "Create the widget holding tabs of groups, each grouptab will contain its vectors"
        devicename = self.app.itemid.devicename
        device = self.app.indiclient[devicename]
        groupset = set(vector.group for vector in device.values() if vector.enable)
        grouplist = list(groupset)
        grouplist.sort()
        with TabbedContent(id="dev_groups"):
            for groupname in grouplist:
                groupid = self.app.itemid.set_group_id(groupname)
                yield GroupTabPane(groupname, groupid)


    def on_group_pane_add_group(self, message: AddGroup) -> None:
        groupname = message.groupname
        groupid = self.app.itemid.set_group_id(groupname)
        tc = self.query_one('#dev_groups')
        tc.add_pane(GroupTabPane(groupname, groupid))


    def on_group_pane_del_vector(self, message: DelVector) -> None:
        vector = message.vector
        vectorid = message.vectorid
        vectorwidget = self.query_one(f"#{vectorid}")
        vectorwidget.remove()
        # remove the vector id's
        self.app.itemid.clear_vector(vector)
        # vector removed, does its group need to be removed?
        groupset = set(v.group for v in vector.device.values() if v.enable)
        # get the group of the deleted vector
        grp = vector.group
        if grp not in groupset:
            # the grp no longer has enabled contents, and must be removed
            grpid = self.app.itemid.get_group_id(grp)
            if grpid is None:
                return
            tc = self.query_one("#dev_groups")
            tc.remove_pane(grpid)
            self.app.itemid.unset_group(vector.devicename, grp)


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

    class ShowLogs(Message):
        """pass messages to the pane."""

        def __init__(self, messagelog: str) -> None:
            self.messagelog = messagelog
            super().__init__()

    def on_mount(self):
        self.clear()
        devicename = self.app.itemid.devicename
        messages = self.app.indiclient[devicename].messages
        if messages:
            self.write_lines( reversed([ localtimestring(t) + "  " + m for t,m in messages]) )
        else:
           self.write(f"Messages from {devicename} will appear here")


    def on_message_log_show_logs(self, message: ShowLogs) -> None:
        if self.line_count < 32:
            self.write_line(message.messagelog)
            return
        # if greater than 32, clear logs, and show the last eight
        # stored as a deque in the device
        self.clear()
        devicename = self.app.itemid.devicename
        messages = self.app.indiclient[devicename].messages
        self.write_lines( reversed([ localtimestring(t) + "  " + m for t,m in messages]) )



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
        self.app.itemid.devicename = None
        self.app.pop_screen()


    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab
