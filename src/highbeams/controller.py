import asyncio
from enum import Enum

from caproto.asyncio.client import Context
from wled import WLED


class Controller:
    """Controls LED strip based on PV values.

    Criteria (in order):

    1. if there is beam in the hutch, set lights to BEAM_PRESENT
    2. if there is no way to open the shutter (e.g. no permit), set lights to NO_PERMIT
    3. if the station is searched, set lights to STATION_READY
    4. set lights to HAS_PERMIT
    """

    class Color(Enum):
        BEAM_PRESENT = (194, 134, 188)
        STATION_READY = (60, 194, 62)
        HAS_PERMIT = (255, 180, 0)
        NO_PERMIT = (255, 0, 0)

    def __init__(
        self, host, beam_present_pv: str, station_searched_pv: str, permit_pv: str
    ):
        self.host = host
        self.pv_names = {
            "beam_present": beam_present_pv,
            "station_searched": station_searched_pv,
            "permit": permit_pv,
        }

    async def connect(self):
        # Connect and monitor the PVs
        ctx = Context()
        pvs = await ctx.get_pvs(*self.pv_names.values())
        self.pvs = {key: pv for key, pv in zip(self.pv_names, pvs)}
        subs = {key: pv.subscribe() for key, pv in self.pvs.items()}
        self.cb_ids = {
            key: sub.add_callback(self.update_lights) for key, sub in subs.items()
        }
        # Set up the WLED connection
        self.wled = WLED(self.host)

    async def update_lights(self, sub, response):
        # Get new values for each PV
        aws = (pv.read() for pv in self.pvs.values())
        values = await asyncio.gather(*aws)
        results = {key: val for key, val in zip(self.pvs.keys(), values)}
        # Set the lights based on PV values
        await self.set_lights(
            beam_present=bool(results["beam_present"]),
            has_permit=bool(results["permit"]),
            station_ready=bool(results["station_search"]),
        )

    async def set_lights(
        self, beam_present: bool, has_permit: bool, station_ready: bool
    ):
        """Retrieve new PV values and set the lights accordingly."""
        if beam_present:
            await self.set_color(self.Color.BEAM_PRESENT)
        elif not has_permit:
            await self.set_color(self.Color.NO_PERMIT)
        elif station_ready:
            await self.set_color(self.Color.STATION_READY)
        else:
            await self.set_color(self.Color.HAS_PERMIT)

    async def set_color(self, color):
        data = {"seg": [{"id": 0, "col": [color._value_]}]}
        await self.wled.request("/json/state", method="POST", data=data)
