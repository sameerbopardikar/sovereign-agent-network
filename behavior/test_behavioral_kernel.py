import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("behavior_eval", ROOT / "evaluate_behavioral_trace.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_contract_has_unique_complete_rule_set():
    contract = json.loads((ROOT / "behavioral-kernel.json").read_text())
    ids = [rule["id"] for rule in contract["rules"]]
    assert len(ids) == len(set(ids)) == 14
    assert ids == [f"BK-{n:02d}" for n in range(1, 15)]
    assert contract["maturity_order"] == MOD.MATURITY


def test_owner_first_positive_trace_passes():
    trace = {
        "trace_id": "positive-owner-first",
        "events": [
            {"type": "owner_intent"},
            {"type": "agent_action", "identity_strength_used": 3, "strongest_identity_strength": 3},
            {"type": "owner_action_requested", "agent_executable": False, "prepared_exact_gate": True},
            {"type": "positive_proof"},
            {"type": "claim", "maturity": "live_verified", "proved_maturity": "live_verified"},
            {"type": "message", "primary_bullets": 3},
            {"type": "verified_outcome"},
            {"type": "terminal_receipt"},
        ],
    }
    result = MOD.evaluate(trace)
    assert result["passed"]
    assert result["violations"] == []
    assert result["metrics"]["owner_actions"] == 1


def test_manual_tutorial_and_false_completion_fail():
    trace = {
        "trace_id": "negative-manual-tutorial",
        "events": [
            {"type": "owner_action_requested", "agent_executable": True, "prepared_exact_gate": False},
            {"type": "claim", "maturity": "live_verified", "proved_maturity": "prepared"},
            {"type": "message", "primary_bullets": 12},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert {"BK-01", "BK-02", "BK-03", "BK-05"} <= rules


def test_avoidable_gate_blocker_identity_and_metric_fail():
    trace = {
        "trace_id": "negative-weak-recovery",
        "events": [
            {"type": "human_gate", "trigger": "avoidable_command_syntax"},
            {"type": "blocker", "fallback_count": 1, "fallback_required": 3},
            {"type": "agent_action", "identity_strength_used": 1, "strongest_identity_strength": 3},
            {"type": "claim", "metric": "page_count"},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert {"BK-04", "BK-06", "BK-07", "BK-13"} <= rules


def test_terminal_loop_chatter_and_unlearned_correction_fail():
    trace = {
        "trace_id": "negative-loop",
        "events": [
            {"type": "terminal_receipt"},
            {"type": "message", "after_terminal": True, "new_human_directive": False},
            {"type": "automation_run", "result": "suggestion_digest"},
            {"type": "correction", "id": "wrong-identity"},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert {"BK-09", "BK-11", "BK-14"} <= rules


def test_correction_with_durable_prevention_passes_that_rule():
    trace = {
        "trace_id": "positive-correction",
        "events": [
            {"type": "correction", "id": "wrong-identity"},
            {"type": "durable_prevention", "correction_id": "wrong-identity"},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-14" not in rules


def test_real_work_proven_claim_without_linked_proof_fails():
    trace = {
        "trace_id": "negative-unlinked-proof",
        "events": [
            {"type": "positive_proof", "event_id": "p1", "result": "success"},
            {"type": "claim", "maturity": "real_work_proven", "proved_maturity": "real_work_proven"},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-05" in rules


def test_real_work_proven_claim_with_failed_linked_proof_fails():
    trace = {
        "trace_id": "negative-failed-proof",
        "events": [
            {"type": "positive_proof", "event_id": "p1", "result": "failed"},
            {
                "type": "claim",
                "maturity": "real_work_proven",
                "proved_maturity": "real_work_proven",
                "proof_event_id": "p1",
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-05" in rules


def test_real_work_proven_claim_with_successful_linked_proof_passes():
    trace = {
        "trace_id": "positive-linked-proof",
        "events": [
            {"type": "positive_proof", "event_id": "p1", "result": "success"},
            {
                "type": "claim",
                "maturity": "real_work_proven",
                "proved_maturity": "real_work_proven",
                "proof_event_id": "p1",
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-05" not in rules


def test_forged_unknown_maturity_value_fails():
    trace = {
        "trace_id": "negative-forged-maturity",
        "events": [
            {
                "type": "claim",
                "maturity": "real_work_proven",
                "proved_maturity": "forged_unknown_state",
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-05" in rules


def test_forged_unknown_claimed_maturity_value_fails():
    trace = {
        "trace_id": "negative-forged-claim",
        "events": [
            {
                "type": "claim",
                "maturity": "forged_unknown_state",
                "proved_maturity": "prepared",
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-05" in rules


def test_finish_line_scope_expansion_after_terminal_lock_fails():
    trace = {
        "trace_id": "negative-scope-expansion",
        "events": [
            {"type": "verified_outcome"},
            {"type": "terminal_receipt", "scope_expanded_after_lock": True},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-08" in rules


def test_terminal_receipt_with_no_verified_outcome_fails():
    trace = {
        "trace_id": "negative-unverified-terminal",
        "events": [
            {"type": "terminal_receipt"},
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-08" in rules


def test_owner_unreachable_without_checkpoint_fails():
    trace = {
        "trace_id": "negative-owner-unreachable",
        "events": [
            {
                "type": "owner_action_requested",
                "agent_executable": False,
                "prepared_exact_gate": True,
                "owner_unreachable": True,
                "checkpoint_preserved": False,
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-10" in rules


def test_owner_unreachable_with_checkpoint_preserved_passes():
    trace = {
        "trace_id": "positive-owner-unreachable-checkpointed",
        "events": [
            {
                "type": "owner_action_requested",
                "agent_executable": False,
                "prepared_exact_gate": True,
                "owner_unreachable": True,
                "checkpoint_preserved": True,
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-10" not in rules


def test_high_friction_action_without_acknowledgment_fails():
    trace = {
        "trace_id": "negative-friction-unacknowledged",
        "events": [
            {
                "type": "agent_action",
                "identity_strength_used": 3,
                "strongest_identity_strength": 3,
                "high_friction_context": True,
                "friction_acknowledged": False,
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-12" in rules


def test_high_friction_action_with_acknowledgment_passes():
    trace = {
        "trace_id": "positive-friction-acknowledged",
        "events": [
            {
                "type": "agent_action",
                "identity_strength_used": 3,
                "strongest_identity_strength": 3,
                "high_friction_context": True,
                "friction_acknowledged": True,
            },
        ],
    }
    rules = {v["rule"] for v in MOD.evaluate(trace)["violations"]}
    assert "BK-12" not in rules
