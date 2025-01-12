

from textual.widgets import Static, Button, Input, Switch
from textual.reactive import reactive
from textual.containers import Container

from .connections import get_connection, set_id, get_last_filename, sendBLOBfile

from indipyclient import getfloat

from textual.widget import Widget

from textual.css.query import NoMatches

from decimal import Decimal

from .filechooser import ChooseFileSc



class SwitchLabel(Static):

    DEFAULT_CSS = """
        SwitchLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """


class SwitchValue(Static):

    DEFAULT_CSS = """
        SwitchValue {
            width: auto;
            padding: 1;
            height: auto;
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
        super().__init__(id=set_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield SwitchLabel(self.member.label)
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
            switch = self.query_one(Switch)
        except NoMatches:
            # presumably this vector has not been displayed yet
            return
        if mvalue == "On":
            switch.value = True
        else:
            switch.value = False


class TextLabel(Static):

    DEFAULT_CSS = """
        TextLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

class ROTextLabel(Static):

    DEFAULT_CSS = """
        ROTextLabel {
            width: 1fr;
            content-align: center middle;
        }
        """

class TextValue(Static):

    DEFAULT_CSS = """
        TextValue {
            width: 1fr;
        }
        """


class ShowText(Container):

    DEFAULT_CSS = """
        ShowText {
            layout: vertical;
            width: 2fr;
            height: auto;
            }

        TextValue {
            width: 1fr;
            padding: 1;
            }

        .textinput {
            layout: horizontal;
            height: auto;
            }

        Button {
            width: auto;
            height: auto;
            }

        """


    def __init__(self, member):
        self.member = member
        super().__init__()

    def compose(self):
        # permission is wo or rw, so show value with editing capbility
        yield TextValue(self.member.membervalue)
        with Container(classes="textinput"):
            yield TextInputField(self.member)
            yield Button("Clear")



class TextMemberPane(Widget):

    DEFAULT_CSS = """
        TextMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=set_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        if self.vector.perm == "ro":
            yield ROTextLabel(self.member.label)
            yield TextValue(self.member.membervalue)
            return
        yield TextLabel(self.member.label)
        yield ShowText(self.member)


    def clear_text_value(self):
        showtextvalue = self.query_one(TextValue)
        showtextvalue.update("")
        self.mvalue = ""

    def watch_mvalue(self, mvalue):
        if mvalue:
            showtextvalue = self.query_one(TextValue)
            showtextvalue.update(mvalue)


    def on_button_pressed(self, event):
        "Clear text input field"
        infld = self.query_one(TextInputField)
        infld.placeholder="Input new text"
        infld.clear()
        event.stop()


class TextInputField(Input):

    DEFAULT_CSS = """
        TextInputField {
            width: 1fr;
            }
        """

    def __init__(self, member):
        self.member = member
        super().__init__(placeholder="Input new text")

    def on_blur(self, event):
        # self.value is the new value input
        if self.value.isprintable():
            checkedvalue = self.value
        else:
            checkedvalue = "Invalid string"
        self.clear()
        self.insert_text_at_cursor(checkedvalue)

    def on_key(self, event):
        if event.character is None:
            return
        # a printable key is pressed
        self.placeholder=""

    def action_submit(self):
        self.screen.focus_next('*')


class LightLabel(Static):

    DEFAULT_CSS = """
        LightLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

class LightValue(Static):

    DEFAULT_CSS = """
        LightValue {
            padding: 1;
            width: auto;
            height: auto;
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
        super().__init__(id=set_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield LightLabel(self.member.label)
        with Container():
            yield LightValue(self.member.membervalue).data_bind(LightMemberPane.mvalue)


class NumberLabel(Static):

    DEFAULT_CSS = """
        NumberLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

class NumberValue(Static):

    DEFAULT_CSS = """
        NumberValue {
            width: 1fr;
            height: 3;
            content-align: center middle;
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

        NumberMemberPane > Container {
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
        super().__init__(id=set_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield NumberLabel(self.member.label)
        yield NumberValue(self.member.membervalue).data_bind(NumberMemberPane.mvalue)
        if self.vector.perm != "ro":
            with Container():
                yield NumberInputField(self.member, placeholder="Input new number")
                yield Button("Clear")

    def on_button_pressed(self, event):
        "Clear number input field"
        infld = self.query_one(NumberInputField)
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



class BLOBLabel(Static):

    DEFAULT_CSS = """
        BLOBLabel {
            width: 1fr;
            content-align: center middle;
        }
        """

class BLOBRxValue(Static):

    DEFAULT_CSS = """
        BLOBRxValue {
            width: 2fr;
        }
        """

    mvalue = reactive("")

    def watch_mvalue(self, mvalue):
        if mvalue:
            self.update(f"RX data: {mvalue}")


class BLOBTxValue(Static):

    DEFAULT_CSS = """
        BLOBTxValue {
            width: 2fr;
        }
        """




class BLOBMemberPane(Widget):

    DEFAULT_CSS = """
        BLOBMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }

        BLOBMemberPane > Container {
            layout: vertical;
            background: $panel;
            width: 2fr;
            height: auto;
            }

        Button {
            margin: 1;
            width: auto;
            height: auto;
            }
        """

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        super().__init__(id=set_id(vector.devicename, vector.name, member.name))


    def compose(self):
        "Draw the member"
        yield BLOBLabel(self.member.label)
        CONNECTION = get_connection()
        last_filename = get_last_filename(self.vector.name, self.member.name)
        with Container():
            if self.vector.perm == "wo":
                yield BLOBRxValue("RX data: N/A -- Write only --").data_bind(BLOBMemberPane.mvalue)
            elif not CONNECTION.blobfolderpath:
                yield BLOBRxValue("RX data: -- BLOB Folder not set --").data_bind(BLOBMemberPane.mvalue)
            elif not self.member.filename:
                yield BLOBRxValue("RX data: -- Nothing yet received --").data_bind(BLOBMemberPane.mvalue)
            else:
                yield BLOBRxValue(f"RX data: {self.member.filename}").data_bind(BLOBMemberPane.mvalue)
            if self.vector.perm == "ro":
                yield BLOBTxValue("TX data: N/A -- Read only --")
            elif last_filename:
                yield BLOBTxValue(f"TX data: {last_filename}")
                yield Button("Send File")
            else:
                yield BLOBTxValue("TX data: -- No file sent --")
                yield Button("Send File")


    def on_button_pressed(self, event):
        "Open file chooser screen"
        def send_path(path):
            if path is not None:
                sendBLOBfile(self.vector.name, self.member.name, path)
                path_text = self.query_one(BLOBTxValue)
                path_text.update(f"TX data: {path.name}")
        self.app.push_screen(ChooseFileSc(), send_path)
        event.stop()
