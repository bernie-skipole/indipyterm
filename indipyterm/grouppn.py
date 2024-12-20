
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id, localtimestring

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BLOBMemberPane

from textual.widget import Widget



class VectorTime(Static):

    DEFAULT_CSS = """
        VectorTime {
            margin-left: 1;
            margin-right: 1;
            width: auto;
        }
        """

    vtime = reactive("")

    def __init__(self, vectortimestamp):
        vectortime = localtimestring(vectortimestamp)
        super().__init__(vectortime)


    def watch_vtime(self, vtime):
        if vtime:
            self.update(vtime)


class VectorState(Static):

    DEFAULT_CSS = """
        VectorState {
            margin-right: 1;
            width: auto;
            }
        """

    vstate = reactive("")

    def __init__(self, vectorstate):
        super().__init__(vectorstate)
        if vectorstate == "Ok":
            self.styles.background = "darkgreen"
            self.styles.color = "white"
        elif vectorstate == "Alert":
            self.styles.background = "red"
            self.styles.color = "white"
        elif vectorstate == "Busy":
            self.styles.background = "yellow"
            self.styles.color = "black"
        elif vectorstate == "Idle":
            self.styles.background = "black"
            self.styles.color = "white"

    def watch_vstate(self, vstate):
        if vstate == "Ok":
            self.styles.background = "darkgreen"
            self.styles.color = "white"
        elif vstate == "Alert":
            self.styles.background = "red"
            self.styles.color = "white"
        elif vstate == "Busy":
            self.styles.background = "yellow"
            self.styles.color = "black"
        elif vstate == "Idle":
            self.styles.background = "black"
            self.styles.color = "white"
        else:
            return
        self.update(vstate)



class VectorTimeState(Widget):

    DEFAULT_CSS = """
        VectorTimeState {
            layout: horizontal;
            align: right top;
            height: 1;
            }

        VectorTimeState > Static {
            width: auto;
            }
        """

    vtime = reactive("")
    vstate = reactive("")

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the timestamp and state"
        yield Static("State:")
        yield VectorTime(self.vector.timestamp).data_bind(VectorTimeState.vtime)
        yield VectorState(self.vector.state).data_bind(VectorTimeState.vstate)


class VectorMessage(Static):

    DEFAULT_CSS = """
        VectorMessage {
            margin-left: 1;
            margin-right: 1;
            height: 2;
            }
        """

    vmessage = reactive("")

    def watch_vmessage(self, vmessage):
        if vmessage:
            self.update(vmessage)


class VectorPane(Widget):

    DEFAULT_CSS = """
        VectorPane {
            layout: vertical;
            height: auto;
            background: $panel;
            border: blue;
            }
        VectorPane > .submitbutton {
            align: right top;
            height: auto;
            }
        VectorPane > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        """

    vtime = reactive("")
    vstate = reactive("")
    vmessage = reactive("")


    def __init__(self, vector):
        self.vector = vector
        self.vector_id = get_id(vector.devicename, vector.name)
        super().__init__(id=self.vector_id)


    def compose(self):
        "Draw the vector"
        self.border_title = self.vector.label

        vts = VectorTimeState(self.vector)
        vts.data_bind(VectorPane.vtime)
        vts.data_bind(VectorPane.vstate)

        yield vts

        # create vector message
        yield VectorMessage(self.vector.message).data_bind(VectorPane.vmessage)

        # show the vector members
        members = self.vector.members()
        for member in members.values():
            if self.vector.vectortype == "SwitchVector":
                yield SwitchMemberPane(self.vector, member)
            if self.vector.vectortype == "TextVector":
                yield TextMemberPane(self.vector, member)
            if self.vector.vectortype == "LightVector":
                yield LightMemberPane(self.vector, member)
            if self.vector.vectortype == "NumberVector":
                yield NumberMemberPane(self.vector, member)
            if self.vector.vectortype == "BLOBVector":
                yield BLOBMemberPane(self.vector, member)

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                yield Button("Submit", id=self.vector_id+"_submit")



class GroupTabPane(TabPane):

    def __init__(self, tabtitle, groupname):
        self.groupname = groupname
        super().__init__(tabtitle)

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        devicename = get_devicename()
        vectors = list(vector for vector in snapshot[devicename].values() if vector.group == self.groupname and vector.enable)
        with VerticalScroll():
            for vector in vectors:
                yield VectorPane(vector)


class GroupPane(Container):

    def compose(self):
        grouplist = get_devicegroups()
        with TabbedContent():
            for groupname in grouplist:
                yield GroupTabPane(groupname, groupname=groupname)



#  how to add and remove groups?
