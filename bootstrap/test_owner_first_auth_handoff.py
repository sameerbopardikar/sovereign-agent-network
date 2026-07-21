import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
SPEC_PATH = ROOT / "owner-first-auth-handoff.json"
MODULE_PATH = ROOT / "validate_owner_first_auth_handoff.py"

spec = importlib.util.spec_from_file_location("owner_first_validator", MODULE_PATH)
assert spec is not None
assert spec.loader is not None
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def write_fixture(tmp_path: Path, data: dict) -> Path:
    target = tmp_path / "protocol.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    return target


def test_canonical_protocol_passes():
    receipt = validator.validate(SPEC_PATH)
    assert receipt["valid"] is True
    assert receipt["required_stage_count"] == 9
    assert receipt["acceptance_check_count"] == 6


def test_missing_live_verification_stage_fails(tmp_path):
    data = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    data["required_stages"].remove("live_capability_verification")
    with pytest.raises(ValueError, match="missing required stages"):
        validator.validate(write_fixture(tmp_path, data))


def test_false_secret_safety_check_fails(tmp_path):
    data = copy.deepcopy(json.loads(SPEC_PATH.read_text(encoding="utf-8")))
    data["acceptance_checks"]["no_secret_in_shared_surfaces"] = False
    with pytest.raises(ValueError, match="invalid acceptance checks"):
        validator.validate(write_fixture(tmp_path, data))


@pytest.mark.parametrize(
    "forbidden_material",
    [
        "password",
        "api_token",
        "private_key",
        "recovery_code",
        "oauth_device_code",
        "cookie",
        "signed_live_browser_url",
    ],
)
def test_missing_required_forbidden_shared_material_fails(tmp_path, forbidden_material):
    data = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    data["forbidden_shared_channel_material"].remove(forbidden_material)

    with pytest.raises(ValueError, match="shared-channel secret prohibition is incomplete"):
        validator.validate(write_fixture(tmp_path, data))
