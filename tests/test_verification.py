from tws_name_changer.services.verification import compare_local_observation

def test_local_match_is_not_independent_verification(device):
    result = compare_local_observation(device, "Example Buds")
    assert result.locally_observed
    assert "independently" in result.message

def test_local_name_mismatch(device):
    assert not compare_local_observation(device, "Other").locally_observed
