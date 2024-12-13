
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BLOBMemberPane



class VectorState(Static):


    vstate = reactive("")

    def __init__(self, vectorstate):
        super().__init__(vectorstate, classes="autowidth", id="vstate")
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


class VectorPane(Container):


    def __init__(self, vector):
        self.vector = vector
        vector_id = get_id(vector.devicename, vector.name)
        super().__init__(id=vector_id)

    def compose(self):
        "Draw the vector"
        with Horizontal(classes="vectortitle"):
            yield Static(self.vector.label, classes="vectorlabel")
            with Horizontal(classes="vectorstate"):
                yield Static("State: ", classes="autowidth" )
                yield VectorState(self.vector.state)

        # create area for vector message
        yield Static(self.vector.message, classes="vectormessage")

        # show the vector members
        members = self.vector.members()
        for member in members.values():
            if self.vector.vectortype == "SwitchVector":
                yield SwitchMemberPane(self.vector, member, classes="memberpane")
            if self.vector.vectortype == "TextVector":
                yield TextMemberPane(self.vector, member, classes="memberpane")
            if self.vector.vectortype == "LightVector":
                yield LightMemberPane(self.vector, member, classes="memberpane")
            if self.vector.vectortype == "NumberVector":
                yield NumberMemberPane(self.vector, member, classes="memberpane")
            if self.vector.vectortype == "BLOBVector":
                yield BLOBMemberPane(self.vector, member, classes="memberpane")




class GroupTabPane(TabPane):

    def __init__(self, tabtitle, devicename, groupname):
        self.devicename = devicename
        self.groupname = groupname
        super().__init__(tabtitle)

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        vectors = list(vector for vector in snapshot[self.devicename].values() if vector.group == self.groupname)
        totalnumber = len(vectors)
        vnumber = 0
        for vector in vectors:
            vnumber += 1
            yield VectorPane(vector)
            if vnumber != totalnumber:
                # if multiple vectors, add a rule between
                yield Rule()


class GroupPane(VerticalScroll):

    devicename = reactive(get_devicename, recompose=True)

    def compose(self):
        grouplist = get_devicegroups(self.devicename)
        with TabbedContent():
            for groupname in grouplist:
                yield GroupTabPane(groupname, devicename=self.devicename, groupname=groupname)


#  how to add and remove groups?
