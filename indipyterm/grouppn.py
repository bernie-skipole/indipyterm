
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BLOBMemberPane



class VectorState(Horizontal):

    vstate = reactive("Alert", recompose=True)

    def compose(self):
        "Draw the vector"
        yield Static("State: ", classes="vstate" )
        state = Static(self.vstate, classes="vstate")
        if self.vstate == "Ok":
            state.styles.background = "darkgreen"
            state.styles.color = "white"
        elif self.vstate == "Alert":
            state.styles.background = "red"
            state.styles.color = "white"
        if self.vstate == "Busy":
            state.styles.background = "yellow"
            state.styles.color = "black"
        yield state




class VectorTitle(Horizontal):

    def __init__(self, vector):
        self.vector = vector
        super().__init__()


    def compose(self):
        "Draw the vector"
        vectorstate = VectorState(classes="vectorstate")
        vectorstate.vstate = self.vector.state
        yield Static(self.vector.label, classes="vectorlabel")
        yield vectorstate




class VectorPane(VerticalScroll):

    def __init__(self, vector):
        self.vector = vector
        super().__init__()


    def compose(self):
        "Draw the vector"
        yield VectorTitle(self.vector)
        yield Static(self.vector.message, classes="vectormessage")

        members = self.vector.members()
        for member in members.values():
            if self.vector.vectortype == "SwitchVector":
                yield SwitchMemberPane(member, classes="memberpane")
            if self.vector.vectortype == "TextVector":
                yield TextMemberPane(member, classes="memberpane")
            if self.vector.vectortype == "LightVector":
                yield LightMemberPane(member, classes="memberpane")
            if self.vector.vectortype == "NumberVector":
                yield NumberMemberPane(member, classes="memberpane")
            if self.vector.vectortype == "BLOBVector":
                yield BLOBMemberPane(member, classes="memberpane")


class GroupTabPane(TabPane):

    devicename = reactive(get_devicename)

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        vectors = list(vector for vector in snapshot[self.devicename].values() if vector.group == self.name)
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
            for group in grouplist:
                yield GroupTabPane(group, name=group).data_bind(GroupPane.devicename)


#  how to add and remove groups?
