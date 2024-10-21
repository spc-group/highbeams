from unittest import mock

import pytest

from highbeams.controller import Controller


@pytest.fixture()
async def controller():
    ctrl = Controller(host="", beam_present_pv="", station_searched_pv="", permit_pv="")
    ctrl.wled = mock.AsyncMock()
    return ctrl


@pytest.mark.asyncio
async def test_beam_present(controller):
    await controller.set_lights(
        beam_present=True, has_permit=False, station_ready=False
    )
    # Were the lights set
    controller.wled.request.assert_called_once_with(
        "/json/state",
        method="POST",
        data={"seg": [{"id": 0, "col": [(194, 134, 188)]}]},
    )


@pytest.mark.asyncio
async def test_no_permit(controller):
    await controller.set_lights(
        beam_present=False, has_permit=False, station_ready=False
    )
    # Were the lights set
    controller.wled.request.assert_called_once_with(
        "/json/state",
        method="POST",
        data={"seg": [{"id": 0, "col": [(255, 0, 0)]}]},
    )


@pytest.mark.asyncio
async def test_station_searched(controller):
    await controller.set_lights(beam_present=False, has_permit=True, station_ready=True)
    # Were the lights set
    controller.wled.request.assert_called_once_with(
        "/json/state",
        method="POST",
        data={"seg": [{"id": 0, "col": [(60, 194, 62)]}]},
    )


@pytest.mark.asyncio
async def test_has_permit(controller):
    await controller.set_lights(
        beam_present=False, has_permit=True, station_ready=False
    )
    # Were the lights set
    controller.wled.request.assert_called_once_with(
        "/json/state",
        method="POST",
        data={"seg": [{"id": 0, "col": [(255, 180, 0)]}]},
    )
