from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Switch
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, get_id

from indipyclient import getfloat

from textual.widget import Widget

from textual.css.query import NoMatches

from decimal import Decimal


class MemberLabel(Static):

    DEFAULT_CSS = """
        MemberLabel {
            width: auto;
            padding: 1;
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



class TextValue(Static):

    DEFAULT_CSS = """
        TextValue {
            width: auto;
            padding: 1;
        }
        """

    mvalue = reactive("")


    def watch_mvalue(self, mvalue):
        if mvalue:
            self.update(mvalue)


class TextMemberPane(Widget):

    DEFAULT_CSS = """
        TextMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }

        TextMemberPane > .onefr {
            width: 1fr;
            height: auto;
            align: center middle;
            }

        TextMemberPane > .twofr {
            layout: vertical;
            width: 2fr;
            height: auto;
            align: center middle;
            }

        TextMemberPane > .twofr > .textinput {
            layout: horizontal;
            height: auto;
            }

        TextMemberPane > .twofr > .textinput > Button {
            width: auto;
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
        with Container(classes="onefr"):
            yield MemberLabel(self.member.label)
        if self.vector.perm == "ro":
            with Container(classes="onefr"):
                yield TextValue(self.member.membervalue).data_bind(TextMemberPane.mvalue)
            return
        # permission is wo or rw
        with Container(classes="twofr"):
            yield TextValue(self.member.membervalue).data_bind(TextMemberPane.mvalue)
            with Container(classes="textinput"):
                yield TextInputField(self.member, placeholder="Input new text")
                yield Button("Clear")

    def on_button_pressed(self, event):
        "Clear text input field"
        infld = self.query_one("TextInputField")
        infld.clear()
        event.stop()


class TextInputField(Input):

    DEFAULT_CSS = """
        TextInputField {
            width: 1fr;
            }
        """

    def __init__(self, member, placeholder):
        self.member = member
        super().__init__(placeholder=placeholder)

    def on_blur(self, event):
        # self.value is the new value input
        if not self.value:
            return
        if self.value.isprintable():
            checkedvalue = self.value
        else:
            checkedvalue = "Invalid string"
        self.clear()
        self.insert_text_at_cursor(checkedvalue)


    def action_submit(self):
        self.screen.focus_next('*')



class LightValue(Static):

    DEFAULT_CSS = """
        LightValue {
            width: auto;
            padding: 1;
        }
        """

    mvalue = reactive("")

    def __init__(self, lightval):
        super().__init__(lightval)
        if lightval == "Ok":
            self.styles.background = "darkgreen"
            self.styles.color = "white"
        elif lightval == "Alert":
            self.styles.background = "red"
            self.styles.color = "white"
        elif lightval == "Busy":
            self.styles.background = "yellow"
            self.styles.color = "black"
        elif lightval == "Idle":
            self.styles.background = "black"
            self.styles.color = "white"

    def watch_mvalue(self, mvalue):
        if mvalue:
            if mvalue == "Ok":
                self.styles.background = "darkgreen"
                self.styles.color = "white"
            elif mvalue == "Alert":
                self.styles.background = "red"
                self.styles.color = "white"
            elif mvalue == "Busy":
                self.styles.background = "yellow"
                self.styles.color = "black"
            elif mvalue == "Idle":
                self.styles.background = "black"
                self.styles.color = "white"
            else:
                mvalue = "?"
                self.styles.background = "black"
                self.styles.color = "white"
            self.update(mvalue)


class LightMemberPane(Widget):

    DEFAULT_CSS = """
        LightMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
        }

        LightMemberPane > Container {
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
            yield LightValue(self.member.membervalue).data_bind(LightMemberPane.mvalue)



class NumberValue(Static):

    DEFAULT_CSS = """
        NumberValue {
            width: auto;
            padding: 1;
        }
        """

    mvalue = reactive("")


    def watch_mvalue(self, mvalue):
        if mvalue:
            self.update(mvalue)


class NumberMemberPane(Widget):

    DEFAULT_CSS = """
        NumberMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }

        NumberMemberPane > .onefr {
            width: 1fr;
            height: auto;
            align: center middle;
            }

        NumberMemberPane > .twofr {
            layout: horizontal;
            width: 2fr;
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
        with Container(classes="onefr"):
            yield MemberLabel(self.member.label)
        with Container(classes="onefr"):
            yield NumberValue(self.member.membervalue).data_bind(NumberMemberPane.mvalue)
        if self.vector.perm != "ro":
            with Container(classes="twofr"):
                yield NumberInputField(self.member, placeholder="Input new number")
                yield Button("Clear")

    def on_button_pressed(self, event):
        "Clear number input field"
        infld = self.query_one("NumberInputField")
        infld.clear()
        event.stop()


class NumberInputField(Input):

    DEFAULT_CSS = """

        NumberInputField {
            width: 1fr;
            }
        """

    def __init__(self, member, placeholder):
        self.member = member
        super().__init__(placeholder=placeholder)

    def on_blur(self, event):
        # self.value is the new value input
        if not self.value:
            return
        try:
            newfloat = getfloat(self.value)
        except (ValueError, TypeError):
            self.clear()
            checkedvalue = self.member.getformattedvalue()
            self.insert_text_at_cursor(checkedvalue)
            return
        # check step, and round newfloat to nearest step value
        stepvalue = getfloat(self.member.step)
        minvalue = getfloat(self.member.min)
        if stepvalue:
            stepvalue = Decimal(str(stepvalue))
            difference = newfloat - minvalue
            newfloat = minvalue + float(int(Decimal(str(difference)) / stepvalue) * stepvalue)
        # check not less than minimum
        if newfloat < minvalue:
            # reset input to be the minimum, and accept this
            self.clear()
            checkedvalue = self.member.getformattedstring(minvalue)
            self.insert_text_at_cursor(checkedvalue)
            return
        if self.member.max != self.member.min:
            maxvalue = getfloat(self.member.max)
            if newfloat > maxvalue:
                # reset input to be the maximum, and accept this
                self.clear()
                checkedvalue = self.member.getformattedstring(maxvalue)
                self.insert_text_at_cursor(checkedvalue)
                return
        # reset input to the correct format, and accept this
        self.clear()
        checkedvalue = self.member.getformattedstring(newfloat)
        self.insert_text_at_cursor(checkedvalue)


    def action_submit(self):
        self.screen.focus_next('*')



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
