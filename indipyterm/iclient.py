
import asyncio, logging

from datetime import datetime, timezone

import indipyclient as ipc


logger = logging.getLogger()
logger.addHandler(logging.NullHandler())



def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"



class ItemID():

    def __init__(self):
        self._itemdict = {}
        self._groupdict = {}
        # Every device, vector, widget will be given an id
        # starting with characters 'id' followed by a string number
        # created by incrementing this self._itemid
        self._itemid = 0

        # devicename needs to be set
        self.devicename = None

    def __bool__(self):
        return bool(self._itemdict)

    def get_group_id(self, groupname):
        if self.devicename is None:
            return
        if not groupname:
            raise KeyError("A group name must be given to get a group id")
        idnumber = self._groupdict.get((self.devicename, groupname))
        if idnumber is None:
            return
        return "gid"+str(idnumber)


    def set_group_id(self, groupname):
        if self.devicename is None:
            return
        if not groupname:
            raise KeyError("A group name must be given to set a group id")
        idnumber = self._groupdict.get((self.devicename, groupname))
        if idnumber is None:
            self._itemid += 1
            self._groupdict[self.devicename, groupname] = self._itemid
            return "gid"+str(self._itemid)
        return "gid"+str(idnumber)


    def unset_group(self, devicename, groupname):
        if not devicename:
            raise KeyError("A devicename must be given to unset a group id")
        if not groupname:
            raise KeyError("A group name must be given to unset a group id")
        self._groupdict[devicename, groupname] = None


    def get_id(self, vectorname=None, membername=None):
        if self.devicename is None:
            return
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        idnumber = self._itemdict.get((self.devicename, vectorname, membername))
        if idnumber is None:
            return
        return "id"+str(idnumber)


    def set_id(self, vectorname=None, membername=None):
        "This create ids for widgets, and returns the id"
        if self.devicename is None:
            return
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        idnumber = self._itemdict.get((self.devicename, vectorname, membername))
        if idnumber is None:
            self._itemid += 1
            self._itemdict[self.devicename, vectorname, membername] = self._itemid
            return "id"+str(self._itemid)
        return "id"+str(idnumber)


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


    def get_devicid(self, devicename):
        if devicename is None:
            return
        idnumber = self._itemdict.get((devicename, None, None))
        if idnumber is None:
            return
        return "id"+str(idnumber)


    def set_devicid(self, devicename):
        "This create id for a device"
        if devicename is None:
            return
        idnumber = self._itemdict.get((devicename, None, None))
        if idnumber is None:
            self._itemid += 1
            self._itemdict[devicename, None, None] = self._itemid
            return "id"+str(self._itemid)
        return "id"+str(idnumber)


    def clear_device(self, device):
        "clear the id's of device, and its vectors and members"
        self.unset(device.devicename)
        for vectorname in device:
            self.unset(device.devicename, vectorname)
            membernamelist = list(device[vectorname].keys())
            for membername in membernamelist:
                self.unset(device.devicename, vectorname, membername)


    def get_devicename(self, deviceid):
        "Given an id, get the devicename, or return None if it does not exist"
        idnumber = int(deviceid.strip("id"))
        for key,value in self._itemdict.items():
            if value == idnumber:
                return key[0]

    def clear(self):
        self._itemdict.clear()
        self._groupdict.clear()
        self._itemid = 0



class IClient(ipc.IPyClient):

    async def rxevent(self, event):
        app = self.clientdata['app']
        startsc = app.get_screen('startsc')

        if (not self.connected) and app.itemid :
            # the connection is disconnected
            if not startsc.is_active:
                app.push_screen('startsc')
            device_pane = startsc.query_one("#device-pane")
            device_pane.post_message(device_pane.ClearDevices())
            app.itemid.clear()

        run_startsc(self, app, startsc, event)

        devicesc = self.clientdata.get('devicesc')
        if devicesc is None:
            return

        run_devicesc(self, app, devicesc, event)


def run_startsc(indiclient, app, startsc, event):
    "handle received events affecting startsc"
    if (event.eventtype == "Define" or event.eventtype == "DefineBLOB"):
        # does this device have an id
        devicename = event.devicename
        if not app.itemid.get_devicid(devicename):
            # it doesn't, so add a button to the devicepane
            device_pane = startsc.query_one("#device-pane")
            device_pane.post_message(device_pane.NewButton(devicename))
    elif (event.eventtype == "Message") and (not event.devicename):
        # This is a system message
        if event.message:
            messagelog = localtimestring(event.timestamp) + "  " + event.message
            messages_pane  = startsc.query_one("#sys-messages-pane")
            messages_pane.post_message(messages_pane.ShowLogs(messagelog))
    elif (event.eventtype == "Delete") and (not indiclient[event.devicename].enable):
        # This entire device should be deleted
        deviceid = app.itemid.get_devicid(event.devicename)
        if not deviceid:
            # This device is not displayed, nothing to do
            return
        # instruct the startsc to remove the device button
        device_pane = startsc.query_one("#device-pane")
        device_pane.post_message(device_pane.DelButton(deviceid))
        if event.message:
            # post this message as a system message, as there is no device
            # so there is nowhere else to show it
            messagelog = localtimestring(event.timestamp) + "  " + event.message
            messages_pane  = startsc.query_one("#sys-messages-pane")
            messages_pane.post_message(messages_pane.ShowLogs(messagelog))
        # remove the button id
        app.itemid.unset(event.devicename)
        # if the startsc is active, remove all id's associated with this device
        if startsc.is_active:
            app.itemid.clear_device(event.device)


def run_devicesc(indiclient, app, devicesc, event):
    "handle received events affecting devicesc"
    devicename = app.itemid.devicename
