
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id, localtimestring

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BLOBMemberPane


class VectorTime(Static):

    vtime = reactive("")

    def __init__(self, vector):
        this_id = f"{get_id(vector.devicename, vector.name)}_vtime"
        vectortime = localtimestring(vector.timestamp)
        super().__init__(vectortime, classes="autowidth", id=this_id)
        self.styles.margin = (0,1,0,1)   # margin 1 on left and right

    def watch_vtime(self, vtime):
        if vtime:
            self.update(vtime)


class VectorState(Static):

    vstate = reactive("")

    def __init__(self, vector):
        this_id = f"{get_id(vector.devicename, vector.name)}_vstate"
        vectorstate = vector.state
        super().__init__(vectorstate, classes="autowidth", id=this_id)
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


class VectorMessage(Static):

    vmessage = reactive("")

    def __init__(self, vector):
        this_id = f"{get_id(vector.devicename, vector.name)}_vmessage"
        vectormessage = vector.message
        super().__init__(vectormessage, classes="vectormessage", id=this_id)

    def watch_vmessage(self, vmessage):
        if vmessage:
            self.update(vmessage)



class VectorPane(Container):


    def __init__(self, vector):
        self.vector = vector
        self.vector_id = get_id(vector.devicename, vector.name)
        super().__init__(id=self.vector_id)
        # this variable sets the height of the pane
        self.pane_height = 8

    def compose(self):
        "Draw the vector"
        self.border_title = self.vector.label
        with Container():
            with Horizontal(classes="vectorstate"):
                yield Static("State:", classes="autowidth" )
                yield VectorTime(self.vector)
                yield VectorState(self.vector)

        # create vector message
        yield VectorMessage(self.vector)

        # show the vector members
        members = self.vector.members()
        for member in members.values():
            if self.vector.vectortype == "SwitchVector":
                switchmember = SwitchMemberPane(self.vector, member, classes="memberpane")
                self.pane_height += switchmember.pane_height
                yield switchmember
            if self.vector.vectortype == "TextVector":
                textmember =  TextMemberPane(self.vector, member, classes="memberpane")
                self.pane_height += textmember.pane_height
                yield textmember
            if self.vector.vectortype == "LightVector":
                lightmember = LightMemberPane(self.vector, member, classes="memberpane")
                self.pane_height += lightmember.pane_height
                yield lightmember
            if self.vector.vectortype == "NumberVector":
                numbermember = NumberMemberPane(self.vector, member, classes="memberpane")
                self.pane_height += numbermember.pane_height
                yield numbermember
            if self.vector.vectortype == "BLOBVector":
                blobmember = BLOBMemberPane(self.vector, member, classes="memberpane")
                self.pane_height += blobmember.pane_height
                yield blobmember

        with Container():
            yield Button("Submit", id=self.vector_id+"_submit", classes="vectorsubmit")

    def on_mount(self):
        # must set the height of the vector pane
        self.styles.height = 15



class GroupTabPane(TabPane):

    def __init__(self, tabtitle, groupname):
        self.groupname = groupname
        super().__init__(tabtitle)

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        devicename = get_devicename()
        vectors = list(vector for vector in snapshot[devicename].values() if vector.group == self.groupname)
        totalnumber = len(vectors)
        vnumber = 0
        with VerticalScroll():
            for vector in vectors:
                vnumber += 1
                yield VectorPane(vector)
                if vnumber != totalnumber:
                    # if multiple vectors, add a rule between
                    yield Rule()


class GroupPane(Container):

    def compose(self):
        grouplist = get_devicegroups()
        with TabbedContent():
            for groupname in grouplist:
                yield GroupTabPane(groupname, groupname=groupname)



#  how to add and remove groups?
