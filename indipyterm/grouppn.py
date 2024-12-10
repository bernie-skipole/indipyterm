
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BLOBMemberPane



class VectorPane(Container):

    vstate = reactive("Alert")

    def __init__(self, vector):
        self.vector = vector
        vector_id = get_id(vector.devicename, vector.name)
        super().__init__(id=vector_id)

    def compose(self):
        "Draw the vector"
        vectorstate = self.vector.state
        with Horizontal(classes="vectortitle"):
            yield Static(self.vector.label, classes="vectorlabel")
            with Horizontal(classes="vectorstate"):
                yield Static("State: ", classes="autowidth" )
                state = Static(vectorstate, classes="autowidth vstate")
                if vectorstate == "Ok":
                    state.styles.background = "darkgreen"
                    state.styles.color = "white"
                elif vectorstate == "Alert":
                    state.styles.background = "red"
                    state.styles.color = "white"
                if vectorstate == "Busy":
                    state.styles.background = "yellow"
                    state.styles.color = "black"
                yield state

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

    def watch_vstate(self, vstate):
        state = self.query_one(".vstate")
        if vstate == "Ok":
            state.styles.background = "darkgreen"
            state.styles.color = "white"
        elif vstate == "Alert":
            state.styles.background = "red"
            state.styles.color = "white"
        if vstate == "Busy":
            state.styles.background = "yellow"
            state.styles.color = "black"
        state.update(vstate)


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
