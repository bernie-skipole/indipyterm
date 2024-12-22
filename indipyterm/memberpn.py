from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Switch
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id

from textual.widget import Widget

from textual.css.query import NoMatches


class MemberLabel(Static):

    DEFAULT_CSS = """
        MemberLabel {
            width: auto;
        }
        """


class SwitchValue(Static):

    DEFAULT_CSS = """
        SwitchValue {
            width: auto;
            padding: 1;
        }
        """

    mvalue = reactive("")

    def __init__(self, switchval):
        super().__init__(switchval)
        if switchval == "On":
            self.styles.background = "darkgreen"
            self.styles.color = "white"
        elif switchval == "Off":
            self.styles.background = "red"
            self.styles.color = "white"
        else:
            self.styles.background = "black"
            self.styles.color = "white"

    def watch_mvalue(self, mvalue):
        if mvalue:
            if mvalue == "On":
                self.styles.background = "darkgreen"
                self.styles.color = "white"
            elif mvalue == "Off":
                self.styles.background = "red"
                self.styles.color = "white"
            else:
                mvalue = "?"
                self.styles.background = "black"
                self.styles.color = "white"
            self.update(mvalue)



class SwitchMemberPane(Widget):

    DEFAULT_CSS = """
        SwitchMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
        }

        SwitchMemberPane > Container {
            width: 1fr;
            height: auto;
            align: center middle;
        }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        with Container():
            yield MemberLabel(self.member.label)
        with Container():
            yield SwitchValue(self.member.membervalue).data_bind(SwitchMemberPane.mvalue)
        with Container():
            if self.member.membervalue == "On":
                if self.vector.perm == "ro":
                    yield Switch(value=True, disabled=True)
                else:
                    yield Switch(value=True)
            else:
                if self.vector.perm == "ro":
                    yield Switch(value=False, disabled=True)
                else:
                    yield Switch(value=False)

    def watch_mvalue(self, mvalue):
        if self.vector.perm != "ro":
            return
        # Only bother changing switch states if ro
        if not  mvalue:
            return
        try:
            switch = self.query_one("Switch")
        except NoMatches:
            # presumably this vector has not been displayed yet
            return
        if mvalue == "On":
            switch.value = True
        else:
            switch.value = False


class TextMemberPane(Widget):

    DEFAULT_CSS = """
        TextMemberPane {
            layout: vertical;
            background: $panel;
            margin-left: 1;
            height: auto;
        }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)



class LightMemberPane(Widget):

    DEFAULT_CSS = """
        LightMemberPane {
            layout: vertical;
            background: $panel;
            margin-left: 1;
            height: auto;
        }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)



class NumberMemberPane(Widget):

    DEFAULT_CSS = """
        NumberMemberPane {
            layout: vertical;
            background: $panel;
            margin-left: 1;
            height: auto;
        }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)


class BLOBMemberPane(Widget):

    DEFAULT_CSS = """
        BLOBMemberPane {
            layout: vertical;
            background: $panel;
            margin-left: 1;
            height: auto;
        }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)
