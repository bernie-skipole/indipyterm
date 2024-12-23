

import asyncio, queue, threading, pathlib, logging

from datetime import datetime, timezone

from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Static, Button
from textual.reactive import reactive
from textual.screen import Screen
from textual.containers import Container, VerticalScroll

from indipyclient.queclient import QueClient

logger = logging.getLogger()
logger.addHandler(logging.NullHandler())


#########################################################################
#
# Global variable _DEVICENAME will be the name of the device
# currently being displayed
#
#########################################################################

_DEVICENAME = ''

#########################################################################
#
# Global variable _DEVICESTATUS will be a status flag
# set to give the progress of the devicescreen
#
#########################################################################

_DEVICESTATUS = 0 # Zero for no devicescreen loaded
                  # 1 for loading in progress
                  # 2 for loaded

##########################################################################
#
# Global variable _CONNECTION will be an instance of the _Connection class
#
##########################################################################

_CONNECTION = None



def get_devicename():
    return _DEVICENAME

def set_devicename(devicename):
    global _DEVICENAME
    _DEVICENAME = devicename



def get_devicestatus():
    return _DEVICESTATUS

def set_devicestatus(value):
    global _DEVICESTATUS, _CONNECTION
    _DEVICESTATUS = value
    if _CONNECTION is None:
        return
    if not value:
        _CONNECTION.devicesc = None


def get_devicemessages(devicename=None):
    "Returns a list of messages for the device"
    if devicename is None:
        devicename = get_devicename()
    if not devicename:
        return
    connection = get_connection()
    snapshot = connection.snapshot
    if not snapshot:
        return
    if devicename not in snapshot:
        return
    messages = snapshot[devicename].messages
    if not messages:
        return
    return reversed([ localtimestring(t) + "  " + m for t,m in messages])


def get_devicegroups(devicename=None):
    "Returns a list of groups for the device"
    if devicename is None:
        devicename = get_devicename()
    if not devicename:
        return
    connection = get_connection()
    snapshot = connection.snapshot
    if not snapshot:
        return
    if devicename not in snapshot:
        return
    device = snapshot[devicename]
    groupset = set(vector.group for vector in device.values() if vector.enable)
    if not groupset:
        return
    grouplist = list(groupset)
    grouplist.sort()
    return grouplist



def make_connection():
    "Creates a singleton _Connection object"
    global _CONNECTION
    if _CONNECTION is None:
        _CONNECTION = _Connection(host='localhost', port=7624, blobfolder=None)

def get_connection():
    return _CONNECTION


def sendvector(vectorname, memberdict):
    global _CONNECTION
    global _DEVICENAME
    if _CONNECTION is None:
        return
    if not _DEVICENAME:
        return
    if _CONNECTION.is_alive():
        _CONNECTION.txque.put((_DEVICENAME, vectorname, memberdict))


class _ItemID():

    def __init__(self):
        self._itemdict = {}
        # Every device, vector, widget will be given an id
        # starting with characters 'id' followed by a string number
        # created by incrementing this self._itemid
        self._itemid = 0

    def set(self, devicename, vectorname=None, membername=None):
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if not devicename:
            raise KeyError("A devicename must be given to set an id")
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        self._itemid += 1
        self._itemdict[devicename, vectorname, membername] = self._itemid
        return self._itemid

    def unset(self, devicename, vectorname=None, membername=None):
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if not devicename:
            raise KeyError("A devicename must be given to unset an id")
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        self._itemdict[devicename, vectorname, membername] = None

    def get(self, devicename, vectorname=None, membername=None):
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if not devicename:
            raise KeyError("A devicename must be given to get an id")
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        return self._itemdict.get((devicename, vectorname, membername))


    def clear(self):
        self._itemdict.clear()
        self._itemid = 0


##################################
#
# Create a global _ItemID
#
###################################

_ITEMID = _ItemID()

def get_id(devicename, vectorname=None, membername=None):
    "This is imported into the gui to create ids for widgets"
    global _ITEMID
    idnumber = _ITEMID.get(devicename, vectorname, membername)
    if idnumber is None:
        return
    return "id"+str(idnumber)

def set_id(devicename, vectorname=None, membername=None):
    "This create ids for widgets, and returns the id"
    global _ITEMID
    idnumber = _ITEMID.get(devicename, vectorname, membername)
    if idnumber is None:
        idnumber = _ITEMID.set(devicename, vectorname, membername)
    return "id"+str(idnumber)



def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"


class _Connection:

    def __init__(self, host=None, port=None, blobfolder=None):

        # create two queues
        # txque to transmit data
        self.txque = queue.Queue(maxsize=4)
        # rxque giving received data
        self.rxque = queue.Queue(maxsize=4)

        self.snapshot = None
        self.queclient = None
        self.clientthread = None
        self.blobfolderpath = None

        if (host == None) or (port == None):
            self.host = None
            self.port = None
            self.hostport = ""
        else:
            self.hostport = f"{host}:{port}"
            self.make_connection(host, port, blobfolder)

        # these are filled in as the app is mounted
        self.app = None
        self.startsc = None
        self.devicesc = None


    def checkhostport(self, hostport):
        """Given a hostport string, Checks it and sets self.hostport
           Returns a string"""
        hostport = hostport.strip()
        if not hostport:
            self.hostport = "localhost:7624"
            return self.hostport

        hostportlist = hostport.split(":")
        if len(hostportlist) != 2:
            host = hostportlist[0].strip()
            if host:
                self.hostport = host +":7624"
            else:
                self.hostport = "localhost:7624"
            return self.hostport
        host = hostportlist[0].strip()
        port = hostportlist[1].strip()
        if not host:
            host = "localhost"
        if not port.isdigit():
            port = "7624"
        self.hostport = f"{host}:{port}"
        return self.hostport


    def checkblobfolder(self, blobfolder):
        """Given a folder, checks it, sets blobfolder, and returns the folder string
           If the given folder is empty, removes the blobfolder
           If the given folder is not a directory, removes the blobfolder and returns
           Invalid Folder"""
        if not blobfolder:
            self.set_BLOBfolder(None)
            return ""
        blobfolder = pathlib.Path(blobfolder).expanduser().resolve()
        if not blobfolder.is_dir():
            self.set_BLOBfolder(None)
            return "Invalid Folder"
        self.set_BLOBfolder(blobfolder)
        return str(blobfolder)


    def set_BLOBfolder(self, blobfolder):
        "Sets blofolder into queclient"
        self.blobfolderpath = blobfolder
        connection = get_connection()
        if not connection.is_alive():
            return
        self.queclient.BLOBfolder = self.blobfolderpath



    def check_rxque(self) -> None:
        """Method to handle received data."""
        global _ITEMID, _DEVICESTATUS

        if _DEVICESTATUS == 1:
            # The device screen is loading
            # don't receive anything just yet
            return

        try:
            item = self.rxque.get_nowait()
        except queue.Empty:
            return
        self.rxque.task_done()

        if not (self.host) or (not self.port):
            self.snapshot = None
            return

        self.snapshot = item.snapshot
        snapshot = self.snapshot

        # system messages
        if (item.eventtype == "Message") and (not item.devicename) and (not item.vectorname):
            log = self.startsc.query_one("#system-messages")
            log.clear()
            messages = snapshot.messages
            mlist = reversed([ localtimestring(t) + "  " + m for t,m in messages ])
            log.write_lines(mlist)

        if not snapshot.connected:
            # the connection is disconnected
            self.clear_devices()
            if not self.startsc.is_active:
                self.app.push_screen('startsc')
            return

        if not item.devicename:
            # possible getProperties or system message which is handled above, just return
            return

        # get currently displayed device
        devicename = get_devicename()


        if item.eventtype == "Delete":  # remove id's
            if item.vectorname:
                # delete the vector id
                _ITEMID.unset(item.devicename, item.vectorname)
                # give every member an empty id
                membernamelist = list(snapshot[item.devicename][item.vectorname].keys())
                for membername in membernamelist:
                    _ITEMID.unset(None, item.devicename, item.vectorname, membername)
                ########## todo, if devicename == item.devicename:recompose devicesc screen
            else:
                # no vectorname, so delete entire device
                deviceid = get_id(item.devicename)
                if deviceid:
                    device_pane = self.startsc.query_one("#device-pane")
                    device_pane.remove_children(deviceid)
                _ITEMID.unset(item.devicename)
                vectornamelist = list(snapshot[item.devicename].keys())
                for vectorname in vectornamelist:
                    _ITEMID.unset(item.devicename, vectorname)
                    membernamelist = list(snapshot[item.devicename][vectorname].keys())
                    for membername in membernamelist:
                        _ITEMID.unset(item.devicename, vectorname, membername)
                if devicename == item.devicename:
                    if not self.startsc.is_active:
                        self.app.push_screen('startsc')
            return

        # add device to startsc on receiving a definition
        if (item.eventtype == "Define" or item.eventtype == "DefineBLOB"):
            # does this device have an id
            if not get_id(item.devicename):
                deviceid = set_id(item.devicename)
                device_pane = self.startsc.query_one("#device-pane")
                device_pane.remove_children("#no-devices")
                device_pane.mount(Button(item.devicename, name=item.devicename, variant="primary", classes="devices", id=deviceid))
                # give the vector an id
                set_id(item.devicename, item.vectorname)
                # give every member an id
                membernamelist = list(snapshot[item.devicename][item.vectorname].keys())
                for membername in membernamelist:
                    set_id(item.devicename, item.vectorname, membername)

            elif not get_id(item.devicename, item.vectorname):
                # known device, but new vector, give the vector an id   ########### todo: add device/vector widget, if device being displayed
                set_id(item.devicename, item.vectorname)
                # give every member an id
                membernamelist = list(snapshot[item.devicename][item.vectorname].keys())
                for membername in membernamelist:
                    set_id(item.devicename, item.vectorname, membername)

        if _DEVICESTATUS != 2:
            # no further action if devicesc not loaded
            return

        if (self.devicesc is None) or self.startsc.is_active:
            # no devicesc shown so return
            return

        if item.devicename != devicename:
            # This device is not currently being shown
            # no need to update any widgets
            return

        # so device which is currently on self.devicesc has been updated
        # update devicesc

        # device messages
        if item.eventtype == "Message" and (not item.vectorname):
            messages = snapshot[devicename].messages
            if messages:
                log = self.devicesc.query_one("#device-messages")
                log.clear()
                mlist = reversed([ localtimestring(t) + "  " + m for t,m in messages ])
                log.write_lines(mlist)

        if not item.vectorname:
            return

        # display the vector timestamp and state
        vectorpane = self.devicesc.query_one(f"#{get_id(devicename, item.vectorname)}")
        vectorpane.vtime = localtimestring(snapshot[devicename][item.vectorname].timestamp)

        if item.eventtype == "TimeOut":
            buttonstatus = self.devicesc.query_one(f"#{get_id(devicename, item.vectorname)}_submitmessage")
            buttonstatus.update("A Timeout Error has occurred")
            vectorpane.vstate = "Alert"
            return

        vectorpane.vstate = snapshot[devicename][item.vectorname].state

        if item.eventtype == "State":
            # Only the state has changed, and that's dealt with
            return

        # Display vector message
        vectorpane.vmessage = snapshot[devicename][item.vectorname].message

        # For every member in the vector, display its value
        vector = snapshot[item.devicename][item.vectorname]
        for membername, membervalue in vector.items():
            memberpane = self.devicesc.query_one(f"#{get_id(devicename, vector.name, membername)}")
            memberpane.mvalue = membervalue


    def connect(self):
        host,port = self.hostport.split(":")
        self.make_connection(host, port, self.blobfolderpath)

    def disconnect(self):
        global _ITEMID
        connection = get_connection()
        if connection.is_alive():
            connection.txque.put(None)
            connection.clientthread.join()
        self.queclient = None
        self.clientthread = None
        self.snapshot = None
        self.host = None
        self.port = None
        log = self.startsc.query_one("#system-messages")
        log.clear()
        t = datetime.now(tz=timezone.utc)
        log.write(localtimestring(t) + "  " + "DISCONNECTED")
        self.clear_devices()


    def clear_devices(self):
        device_pane = self.startsc.query_one("#device-pane")
        if device_pane.query(".devices"):
            device_pane.remove_children(".devices")
            device_pane.mount(Static("No Devices found", id="no-devices"))
        _ITEMID.clear()



    def make_connection(self, host, port, blobfolder=None):
        if (self.clientthread is not None) and self.clientthread.is_alive():
            raise RuntimeError("Connection has to terminate before another one can be added")
        # The calling app sets the snapshot here
        self.snapshot = None
        self.queclient = None
        self.clientthread = None
        self.host = host
        self.port = port

        if blobfolder:
            # if no blobfolder given, self.blobfolderpath remains unchanged
            if isinstance(blobfolder, pathlib.Path):
                self.blobfolderpath = blobfolder
            else:
                self.blobfolderpath = pathlib.Path(blobfolder).expanduser().resolve()
            if not self.blobfolderpath.is_dir():
                raise KeyError("If given, the BLOB's folder should be an existing directory")


        if self.host and self.port:
            # empty queues
            while not self.txque.empty():
                try:
                    item = self.txque.get_nowait()
                except queue.Empty:
                    break
            while not self.rxque.empty():
                try:
                    item = self.rxque.get_nowait()
                except queue.Empty:
                    break
            # create a QueClient object
            self.queclient = QueClient(self.txque, self.rxque, self.host, self.port, self.blobfolderpath)
            # create a thread to run self.queclient.asyncrun()
            self.clientthread = threading.Thread(target=asyncio.run, args=(self.queclient.asyncrun(),))
            self.clientthread.start()


    def is_alive(self):
        if self.clientthread is None:
            return False
        if self.clientthread.is_alive():
            return True
        self.queclient = None
        self.clientthread = None
        self.snapshot = None
