#!/usr/bin/env python3
"""Validate the portable owner-first authentication bootstrap contract."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_STAGES = {
    "environment_discovery",
    "agent_side_preparation",
    "approved_secret_store_selection",
    "direct_handoff_creation",
    "irreducible_human_gate_only",
    "agent_side_completion",
    "runtime_secret_retrieval",
    "live_capability_verification",
    "secret_free_receipt",
}
REQUIRED_CHECKS = {
    "direct_exact_gate_handoff",
    "agent_auto_resume",
    "no_secret_in_shared_surfaces",
    "runtime_secret_retrieval_verified",
    "real_authenticated_action_verified",
    "scope_revocation_recovery_recorded",
}
REQUIRED_FORBIDDEN_SHARED_MATERIAL = {
    "password",
    "api_token",
    "private_key",
    "recovery_code",
    "oauth_device_code",
    "cookie",
    "signed_live_browser_url",
}


def validate(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("protocol") != "owner-first-auth-handoff":
        raise ValueError("unexpected protocol identity")

    stages = set(data.get("required_stages", []))
    missing_stages = REQUIRED_STAGES - stages
    if missing_stages:
        raise ValueError(f"missing required stages: {sorted(missing_stages)}")

    checks = data.get("acceptance_checks", {})
    missing_checks = REQUIRED_CHECKS - set(checks)
    false_checks = sorted(name for name in REQUIRED_CHECKS if checks.get(name) is not True)
    if missing_checks or false_checks:
        raise ValueError(
            f"invalid acceptance checks: missing={sorted(missing_checks)} false={false_checks}"
        )

    forbidden = set(data.get("forbidden_shared_channel_material", []))
    if not REQUIRED_FORBIDDEN_SHARED_MATERIAL <= forbidden:
        raise ValueError("shared-channel secret prohibition is incomplete")

    states = data.get("completion_states", [])
    if states != ["prepared", "human_gate_waiting", "authenticated", "live_verified"]:
        raise ValueError("completion states must preserve the maturity boundary")

    return {
        "valid": True,
        "protocol": data["protocol"],
        "version": data["version"],
        "required_stage_count": len(REQUIRED_STAGES),
        "acceptance_check_count": len(REQUIRED_CHECKS),
    }


if __name__ == "__main__":
    source = Path(__file__).with_name("owner-first-auth-handoff.json")
    print(json.dumps(validate(source), sort_keys=True))
