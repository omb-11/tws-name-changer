import pytest
from tws_name_changer.bluetooth.discovery import _clean_name
from tws_name_changer.bluetooth.device_info import display_name

def test_clean_name_removes_control_characters():
    assert _clean_name(" Bud\x00s\n ") == "Buds"

def test_clean_name_missing_is_missing():
    assert _clean_name(None) is None

def test_display_name_for_missing_name(device):
    assert display_name(device.__class__(**{**device.__dict__, "name": None})) == "Unnamed Bluetooth device"
