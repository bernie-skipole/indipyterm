from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id

from textual.widget import Widget


class SwitchMemberPane(Widget):

    DEFAULT_CSS = """
        SwitchMemberPane {
            layout: vertical;
            background: $panel;
            margin-left: 1;
            height: auto;
        }
        """

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)
        yield Static(f"Value : {self.member.membervalue}")



class TextMemberPane(Widget):

    DEFAULT_CSS = """
        TextMemberPane {
            layout: vertical;
            background: $panel;
            margin-left: 1;
            height: auto;
        }
        """

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

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=get_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)
