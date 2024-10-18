import asyncio
from enum import Enum

from caproto.asyncio.client import Context
from wled import WLED


class BeamlineLights():
    class Color(Enum):
        BEAM_PRESENT = (194, 134, 188)
        STATION_READY = (60, 194, 62)
        HAS_PERMIT = ()
        NO_PERMIT = ()
    
    def __init__(self, host: str, beam_present_pv):
        self.host = host
        self.beam_present_pv = beam_present_pv

    async def connect(self):
        ctx = Context()
        beam_present, = await ctx.get_pvs(self.beam_present_pv)
        beam_present_sub = beam_present.subscribe()
        beam_present_sub.add_callback(self.set_beam_present)
        # Set up the WLED connection
        self.wled = WLED(self.host)

    async def set_beam_present(self, sub, response):
        print(response.data[0])
        if response.data[0]:
            # await self.wled.segment(0, color_primary=self.Color.BEAM_PRESENT)
            color = self.Color.BEAM_PRESENT
        else:
            # await self.wled.segment(0, color_primary=self.Color.STATION_READY)
            color = self.Color.STATION_READY
        data = {"seg": [{
            "id": 0,
            "col": [color._value_]
            }]
                }
        await self.wled.request("/json/state", method="POST", data = data)

async def set_beam_present(sub, response):
    print(response.data[0])

async def main():
    lights = BeamlineLights(host="wled-25idc.xray.aps.anl.gov", beam_present_pv='S25ID-PSS:StaC:BeamPresentM')
    await lights.connect()
    while True:
        await asyncio.sleep(0.01)
    await lights.disconnect()


print(__name__)

if __name__ == "__main__":
    asyncio.run(main())
