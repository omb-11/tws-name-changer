from datetime import datetime, timezone
import pytest
from tws_name_changer.bluetooth.base import DeviceObservation, Transport

@pytest.fixture
def device() -> DeviceObservation:
    return DeviceObservation("ble:test", "Example Buds", "AA:BB", Transport.BLE, -60, datetime.now(timezone.utc))
