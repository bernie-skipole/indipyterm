# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///


"""Two switch devices. The second initially disabled and gets added a few seconds after starting
   to test that adding a device works"""


import asyncio

import indipydriver as ipd



class Driver(ipd.IPyDriver):
    """IPyDriver is subclassed here"""

    async def hardware(self):
        """Send a new ro switch value every second"""

        device1 = self['device1']
        device2 = self['device2']

        vector1 = self['device1']['vector1']
        vector2 = self['device2']['vector2']

        switchA = vector1['switchA']
        switchB = vector1['switchB']
        switchC = vector2['switchC']
        switchD = vector2['switchD']


        def changeswitches():
            "Change all switch values"
            nonlocal vector1, vector2, switchA, switchB, switchC, switchD
            switchA = 'On' if switchA == 'Off' else 'Off'
            switchB = 'On' if switchB == 'Off' else 'Off'
            switchC = 'On' if switchC == 'Off' else 'Off'
            switchD = 'On' if switchD == 'Off' else 'Off'
            vector1['switchA'] = switchA
            vector1['switchB'] = switchB
            vector2['switchC'] = switchC
            vector2['switchD'] = switchD

        while not self.stop:
            for i in range(5):
                # do this five times
                await asyncio.sleep(3)
                # change switches
                changeswitches()
                if device1.enable:
                    await vector1.send_setVector()
                if device2.enable:
                    await vector2.send_setVector()
            if device2.enable:
                # delete device 2
                await device2.send_delProperty(message="Device2 deleted")
            else:
                # enable device2, and send its vector definition
                device2.enable = True
                await vector2.send_defVector(message='device2, vector 2 enabled')


def make_switch_driver():

    switchA = ipd.SwitchMember( name="switchA",
                                membervalue='On' )

    switchB = ipd.SwitchMember( name="switchB",
                                membervalue='On' )

    vector1 = ipd.SwitchVector( name = 'vector1',
                                label = 'vector1',
                                group = 'Test1',
                                perm = "ro",
                                state = "Ok",
                                rule = "AnyOfMany",
                                switchmembers = [switchA, switchB])

    switchC = ipd.SwitchMember( name="switchC",
                                membervalue='On' )

    switchD = ipd.SwitchMember( name="switchD",
                                membervalue='On' )

    vector2 = ipd.SwitchVector( name = 'vector2',
                                label = 'vector2',
                                group = 'Test2',
                                perm = "ro",
                                state = "Ok",
                                rule = "AnyOfMany",
                                switchmembers = [switchC, switchD])


    # create devices with these vectors
    device1 = ipd.Device( devicename='device1',
                          properties=[vector1] )

    device2 = ipd.Device( devicename='device2',
                          properties=[vector2] )

    # start with device2 disabled
    device2.enable = False

    return Driver(device1, device2)


if __name__ == "__main__":

    # Make drivers
    switchdriver = make_switch_driver()

    server = ipd.IPyServer(switchdriver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
