import asyncio

from .controller import Controller


async def main():
    lights = Controller(
        host="wled-25idc.xray.aps.anl.gov",
        beam_present_pv="S25ID-PSS:StaC:BeamPresentM",
        station_searched_pv="S25ID-PSS:StaC:SecureM",
        permit_pv="SR-ACIS:25ID:FesPermitM",
    )
    await lights.connect()
    # Loop until interrupted
    while True:
        await asyncio.sleep(0.01)
    await lights.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
