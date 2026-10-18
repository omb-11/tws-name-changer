import asyncio
import pytest
from tws_name_changer.bluetooth.base import RenameStatus
from tws_name_changer.services.rename_service import RenameService, validate_name

def test_unsupported_device_receives_no_command(device):
    result = asyncio.run(RenameService().request_rename(device, "My Buds"))
    assert result.status is RenameStatus.NOT_SUPPORTED
    assert "No command was sent" in result.message

@pytest.mark.parametrize("name", ["", "  ", "bad\nname"])
def test_invalid_names_are_rejected(name):
    assert validate_name(name) is not None

def test_name_is_limited_by_utf8_bytes():
    assert validate_name("é" * 125) is not None
