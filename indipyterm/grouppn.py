
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups


class GroupTabPane(TabPane):

    devicename = reactive(get_devicename)

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        for vector in snapshot[self.devicename].values():
            if vector.group == self.name:
                yield Static(vector.label)
                for membervalue in vector.values():
                    yield Static(membervalue)




class GroupPane(VerticalScroll):

    devicename = reactive(get_devicename, recompose=True)

    def compose(self):
        grouplist = get_devicegroups(self.devicename)
        with TabbedContent():
            for group in grouplist:
                yield GroupTabPane(group, name=group).data_bind(GroupPane.devicename)
