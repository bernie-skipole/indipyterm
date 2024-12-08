from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups


class SwitchMemberPane(VerticalScroll):

    def __init__(self, member, classes):
        self.member = member
        super().__init__(classes=classes, id=member.user_string)


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)
        yield Static(f"Value : {self.member.membervalue}")



class TextMemberPane(VerticalScroll):

    def __init__(self, member, classes):
        self.member = member
        super().__init__(classes=classes, id=member.user_string)


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)



class LightMemberPane(VerticalScroll):

    def __init__(self, member, classes):
        self.member = member
        super().__init__(classes=classes, id=member.user_string)


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)



class NumberMemberPane(VerticalScroll):

    def __init__(self, member, classes):
        self.member = member
        super().__init__(classes=classes, id=member.user_string)


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)


class BLOBMemberPane(VerticalScroll):

    def __init__(self, member, classes):
        self.member = member
        super().__init__(classes=classes, id=member.user_string)


    def compose(self):
        "Draw the member"
        yield Static(self.member.label)
