# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///


"""Several SwitchVectors illustrating switch rules
   OneOfMany AtMostOne AnyOfMany and ReadOnly"""


import asyncio

import indipydriver as ipd


class SwitchDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here"""

    async def rxevent(self, event):
        """On receiving data."""

        devicename = self.driverdata['devicename']

        match event:

            case ipd.newSwitchVector(devicename=devicename):
                # get the received values and set them into the vector
                for membername, membervalue in event.items():
                    event.vector[membername] = membervalue
                # transmit the vector back to client to confirm received
                await event.vector.send_setVector()


    async def hardware(self):
        """Send a new ro switch value every second"""

        devicename = self.driverdata['devicename']

        rovector = self[devicename]['ROvector']
        while not self.stop:
            # send a new switch value every second
            for s in range(5):
                await asyncio.sleep(1)
                if rovector[f"ROMmember{s}"] == "On":
                    rovector[f"ROMmember{s}"] = "Off"
                else:
                    rovector[f"ROMmember{s}"] = "On"
                await rovector.send_setVector()


def make_switch_driver(devicename):
    "Returns an instance of the driver"

    # create five members with rule OneOfMany

    oom_members = []
    for s in range(5):
        # One member must be On
        if s:
            memval = "Off"
        else:
            memval = "On"

        member = ipd.SwitchMember( name=f"OOMmember{s}",
                                   label=f"Switch {s}",
                                   membervalue=memval )
        oom_members.append(member)


    oom_vector = ipd.SwitchVector( name = 'OOMvector',
                                   label = "Switch",
                                   group = 'OneOfMany',
                                   perm = "wo",
                                   state = "Ok",
                                   rule = "OneOfMany",
                                   switchmembers = oom_members)

    # create five members with rule AtMostOne
    amo_members = []
    for s in range(5):
        member = ipd.SwitchMember( name=f"AMOmember{s}",
                                   label=f"Switch {s}",
                                   membervalue="Off" )
        amo_members.append(member)


    amo_vector = ipd.SwitchVector( name = 'AMOvector',
                                   label = "Switch",
                                   group = 'AtMostOne',
                                   perm = "wo",
                                   state = "Ok",
                                   rule = "AtMostOne",
                                   switchmembers = amo_members)

    # create five members with rule AnyOfMany
    aom_members = []
    for s in range(5):
        member = ipd.SwitchMember( name=f"AOMmember{s}",
                                   label=f"Switch {s}",
                                   membervalue="Off" )
        aom_members.append(member)


    aom_vector = ipd.SwitchVector( name = 'AOMvector',
                                   label = "Switch",
                                   group = 'AnyOfMany',
                                   perm = "wo",
                                   state = "Ok",
                                   rule = "AnyOfMany",
                                   switchmembers = aom_members)

    # create Read Only vector that the client cannot change
    # this will be continuously altered by the driver hardware method
    # to simulate an instrument having switches locally controlled

    ro_members = []
    for s in range(5):
        # Set first member On
        if s:
            memval = "Off"
        else:
            memval = "On"

        member = ipd.SwitchMember( name=f"ROMmember{s}",
                                   label=f"Switch {s}",
                                   membervalue=memval )
        ro_members.append(member)

    ro_vector = ipd.SwitchVector( name = 'ROvector',
                                   label = "Switch",
                                   group = 'ReadOnly',
                                   perm = "ro",
                                   state = "Ok",
                                   rule = "AnyOfMany",
                                   switchmembers = ro_members)


    # create a device with these vectors
    switchingdevice = ipd.Device( devicename=devicename,
                         properties=[oom_vector, amo_vector, aom_vector, ro_vector] )

    # Create the Driver, containing this Device
    driver = SwitchDriver( switchingdevice, devicename=devicename)

    # and return the driver
    return driver



class LightDriver(ipd.IPyDriver):
    """IPyDriver is subclassed here
       It has device 'bincounter' with a light 'binvector'
       with four members 'binvalue0' to 'binvalue3'
       which it populates with counting binary lights"""

    async def hardware(self):
        """Sends the counting binvector with four members
           showing red lights (Alert) for binary 1
           and green lights (Ok) for binary 0
           Then does the same again, but with Busy and Idle lights"""

        devicename = self.driverdata['devicename']

        binvector = self[devicename]['binvector']
        while not self.stop:
            # send a new lights count every second
            for n in range(16):
                await asyncio.sleep(1)
                binstring = f'{n:04b}'       # strings "0000" to "1111" generated as n increments
                binvector['binvalue0'] = "Alert" if binstring[3] == "1" else "Ok"
                binvector['binvalue1'] = "Alert" if binstring[2] == "1" else "Ok"
                binvector['binvalue2'] = "Alert" if binstring[1] == "1" else "Ok"
                binvector['binvalue3'] = "Alert" if binstring[0] == "1" else "Ok"
                await binvector.send_setVector()
            for n in range(16):
                await asyncio.sleep(1)
                binstring = f'{n:04b}'       # strings "0000" to "1111" generated as n increments
                binvector['binvalue0'] = "Idle" if binstring[3] == "1" else "Busy"
                binvector['binvalue1'] = "Idle" if binstring[2] == "1" else "Busy"
                binvector['binvalue2'] = "Idle" if binstring[1] == "1" else "Busy"
                binvector['binvalue3'] = "Idle" if binstring[0] == "1" else "Busy"
                await binvector.send_setVector()



def make_light_driver(devicename):
    "Returns an instance of the driver"

    # create four LightMembers, binvalue0 to binvalue3
    members= []
    for m in range(4):
        members.append( ipd.LightMember( name = f"binvalue{m}",
                                         label = f"Light {m}" )  )


    # create a vector containing these members
    binvector = ipd.LightVector( name="binvector",
                                 label="Light Counter",
                                 group="Values",
                                 state="Ok",
                                 lightmembers=members )

    # create a device with this vector
    bincounter = ipd.Device( devicename=devicename,
                             properties=[binvector] )

    # Create the Driver, containing this Device
    driver = LightDriver( bincounter, devicename=devicename )

    # and return the driver
    return driver



if __name__ == "__main__":

    switchdriver = make_switch_driver("switches")
    lightdriver = make_light_driver("lights")
    server = ipd.IPyServer(switchdriver, lightdriver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
