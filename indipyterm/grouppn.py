
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button, Log, Input, TabbedContent, TabPane, Rule
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll, Center

from .connections import get_connection, get_devicename, get_devicemessages, get_devicegroups, set_id, get_id, localtimestring, sendvector, get_devicestatus, set_devicestatus, set_group_id

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BLOBMemberPane

from textual.widget import Widget



class GroupTabPane(TabPane):

    def __init__(self, tabtitle, groupname):
        self.groupname = groupname
        super().__init__(tabtitle, id=set_group_id(groupname))

    def compose(self):
        "For every vector draw it"
        snapshot = get_connection().snapshot
        devicename = get_devicename()
        vectors = list(vector for vector in snapshot[devicename].values() if vector.group == self.groupname and vector.enable)
        with VerticalScroll():
            for vector in vectors:
                yield VectorPane(vector)

    def add_vector(self, vector):
        "Add a vector to this tab"
        # get the VerticalScroll
        vs = self.query_one('VerticalScroll')
        vs.mount(VectorPane(vector))





class GroupPane(Container):

    DEFAULT_CSS = """

        GroupPane {
            width: 100%;
            padding: 1;
            min-height: 10;
            }
        """

    def compose(self):
        grouplist = get_devicegroups()
        with TabbedContent(id="dev_groups"):
            for groupname in grouplist:
                yield GroupTabPane(groupname, groupname=groupname)



#  how to add and remove groups?



class VectorTime(Static):

    DEFAULT_CSS = """
        VectorTime {
            margin-left: 1;
            margin-right: 1;
            width: auto;
        }
        """

    vtime = reactive("")

    def __init__(self, vectortimestamp):
        vectortime = localtimestring(vectortimestamp)
        super().__init__(vectortime)


    def watch_vtime(self, vtime):
        if vtime:
            self.update(vtime)


class VectorState(Static):

    DEFAULT_CSS = """
        VectorState {
            margin-right: 1;
            width: auto;
            }
        """

    vstate = reactive("")

    def __init__(self, vectorstate):
        super().__init__(vectorstate)
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



class VectorTimeState(Widget):

    DEFAULT_CSS = """
        VectorTimeState {
            layout: horizontal;
            align: right top;
            height: 1;
            }

        VectorTimeState > Static {
            width: auto;
            }
        """

    vtime = reactive("")
    vstate = reactive("")

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the timestamp and state"
        yield Static("State:")
        yield VectorTime(self.vector.timestamp).data_bind(VectorTimeState.vtime)
        yield VectorState(self.vector.state).data_bind(VectorTimeState.vstate)


class VectorMessage(Static):

    DEFAULT_CSS = """
        VectorMessage {
            margin-left: 1;
            margin-right: 1;
            height: 2;
            }
        """

    vmessage = reactive("")

    def watch_vmessage(self, vmessage):
        if vmessage:
            self.update(vmessage)


class VectorPane(Widget):

    DEFAULT_CSS = """
        VectorPane {
            layout: vertical;
            height: auto;
            background: $panel;
            border: mediumvioletred;
            }
        """

    vtime = reactive("")
    vstate = reactive("")
    vmessage = reactive("")


    def __init__(self, vector):
        self.vector = vector
        vector_id = set_id(vector.devicename, vector.name)
        super().__init__(id=vector_id)


    def compose(self):
        "Draw the vector"
        self.border_title = self.vector.label

        vts = VectorTimeState(self.vector)
        vts.data_bind(VectorPane.vtime)
        vts.data_bind(VectorPane.vstate)

        yield vts

        # create vector message
        yield VectorMessage(self.vector.message).data_bind(VectorPane.vmessage)

        if self.vector.vectortype == "SwitchVector":
            yield SwitchVector(self.vector)
        elif self.vector.vectortype == "TextVector":
            yield TextVector(self.vector)
        elif self.vector.vectortype == "LightVector":
            yield LightVector(self.vector)
        elif self.vector.vectortype == "NumberVector":
            yield NumberVector(self.vector)
        elif self.vector.vectortype == "BLOBVector":
            yield BLOBVector(self.vector)



class SwitchVector(Widget):

    DEFAULT_CSS = """
        SwitchVector {
            height: auto;
            }
        SwitchVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        SwitchVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        SwitchVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }

        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the switch vector members"
        members = self.vector.members()
        for member in members.values():
            yield SwitchMemberPane(self.vector, member)

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                yield Static("", id=f"{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
                yield Button("Submit")


    def on_switch_changed(self, event):
        """Enforce the rule, OneOfMany AtMostOne AnyOfMany"""
        if self.vector.perm == "ro":
            # ignore switch changes for read only vectors
            return
        devicestatus = get_devicestatus()
        if devicestatus != 2:
            return
        buttonstatus = self.query_one(f"#{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
        buttonstatus.update("")
        if self.vector.rule == "AnyOfMany":
            return
        if not event.value:
            # switch turned off
            return
        switches = self.query("Switch")
        for s in switches:
            if s is event.switch:
                # s is the switch changed
                continue
            if s.value:
                # any switch other than the one changed must be off
                s.value = False


    def on_button_pressed(self, event):
        "Get membername:value dictionary"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        devicestatus = get_devicestatus()
        if devicestatus != 2:
            return
        buttonstatus = self.query_one(f"#{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
        switchpanes = self.query("SwitchMemberPane")
        memberdict = {}
        for sp in switchpanes:
            membername = sp.member.name
            switch = sp.query_one("Switch")
            if switch.value:
                memberdict[membername] = "On"
            else:
                memberdict[membername] = "Off"
        # Check at least one pressed if rule is OneOfMany
        if self.vector.rule == "OneOfMany":
            oncount = list(memberdict.values()).count("On")
            if oncount != 1:
                buttonstatus.update("Invalid, OneOfMany rule requires one On switch")
                return
        # Check no more than one pressed if rule is AtMostOne
        if self.vector.rule == "AtMostOne":
            oncount = list(memberdict.values()).count("On")
            if oncount > 1:
                buttonstatus.update("Invalid, AtMostOne rule allows only one On switch")
                return
        # send this to the server
        buttonstatus.update("")
        sendvector(self.vector.name, memberdict)




class TextVector(Widget):

    DEFAULT_CSS = """
        TextVector {
            height: auto;
            }

        TextVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        TextVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        TextVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }

        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the number vector members"
        members = self.vector.members()
        for member in members.values():
            yield TextMemberPane(self.vector, member)

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                yield Static("", id=f"{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
                yield Button("Submit")

    def on_button_pressed(self, event):
        "Get membername:value dictionary"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        devicestatus = get_devicestatus()
        if devicestatus != 2:
            return
        buttonstatus = self.query_one(f"#{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
        textpanes = self.query("TextMemberPane")
        memberdict = {}
        for tp in textpanes:
            membername = tp.member.name
            textfield = tp.query_one("TextInputField")
            if textfield.placeholder:
                continue
            memberdict[membername] = textfield.value
        # send this to the server
        buttonstatus.update("")
        sendvector(self.vector.name, memberdict)


class LightVector(Widget):

    DEFAULT_CSS = """
        LightVector {
            height: auto;
            }
        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the light vector"
        members = self.vector.members()
        for member in members.values():
            yield LightMemberPane(self.vector, member)


class NumberVector(Widget):

    DEFAULT_CSS = """
        NumberVector {
            height: auto;
            }

        NumberVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        NumberVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        NumberVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }

        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the number vector members"
        members = self.vector.members()
        for member in members.values():
            yield NumberMemberPane(self.vector, member)

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                yield Static("", id=f"{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
                yield Button("Submit")

    def on_button_pressed(self, event):
        "Get membername:value dictionary"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        devicestatus = get_devicestatus()
        if devicestatus != 2:
            return
        buttonstatus = self.query_one(f"#{get_id(self.vector.devicename, self.vector.name)}_submitmessage")
        numberpanes = self.query("NumberMemberPane")
        memberdict = {}
        for np in numberpanes:
            membername = np.member.name
            numberfield = np.query_one("NumberInputField")
            if not numberfield.value:
                continue
            memberdict[membername] = numberfield.value
        # send this to the server
        buttonstatus.update("")
        sendvector(self.vector.name, memberdict)


class BLOBVector(Widget):

    DEFAULT_CSS = """
        BLOBVector {
            height: auto;
            }
        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the BLOB vector"
        members = self.vector.members()
        for member in members.values():
            yield BLOBMemberPane(self.vector, member)
