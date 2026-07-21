#!/usr/bin/env python3
"""Deterministically evaluate observable agent traces against SAN behavior invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path

MATURITY = ["prepared", "connected", "tested", "live_verified", "real_work_proven"]


def evaluate(trace: dict) -> dict:
    events = trace.get("events", [])
    violations: list[dict[str, str]] = []

    def add(rule: str, detail: str) -> None:
        violations.append({"rule": rule, "detail": detail})

    for event in events:
        if event.get("type") == "owner_action_requested" and event.get("agent_executable", False):
            add("BK-01", "Agent delegated agent-executable work to the owner")
        if event.get("type") == "owner_action_requested" and not event.get("prepared_exact_gate", False):
            add("BK-02", "Owner request was not positioned at one prepared exact gate")
        if event.get("type") == "claim":
            claimed = event.get("maturity")
            proved = event.get("proved_maturity", "prepared")
            if claimed is not None and claimed not in MATURITY:
                add("BK-05", f"Claimed maturity '{claimed}' is not a canonical maturity value")
            elif proved not in MATURITY:
                add("BK-05", f"Proved maturity '{proved}' is not a canonical maturity value")
            elif claimed in MATURITY and MATURITY.index(claimed) > MATURITY.index(proved):
                add("BK-05", f"Claimed {claimed} but evidence supports only {proved}")
            elif claimed == "real_work_proven":
                claim_id = event.get("proof_event_id")
                linked_proofs = []
                if claim_id is not None:
                    linked_proofs = [
                        e for e in events
                        if e.get("type") == "positive_proof" and e.get("event_id") == claim_id
                    ]
                if not linked_proofs:
                    add("BK-05", "real_work_proven claim has no linked positive_proof event")
                elif len(linked_proofs) > 1:
                    add(
                        "BK-05",
                        f"real_work_proven claim's proof_event_id '{claim_id}' matches "
                        f"{len(linked_proofs)} positive_proof events with duplicate/conflicting IDs",
                    )
                elif linked_proofs[0].get("result") != "success":
                    add(
                        "BK-05",
                        "real_work_proven claim's linked proof does not have an explicit "
                        f"successful result (result={linked_proofs[0].get('result')!r})",
                    )
        if event.get("type") == "blocker" and event.get("fallback_count", 0) < event.get("fallback_required", 1):
            add("BK-07", "Blocker surfaced before required fallback depth")
        if event.get("type") == "human_gate" and event.get("trigger") == "avoidable_command_syntax":
            add("BK-06", "Avoidable command syntax was escalated instead of redesigned")
        if event.get("type") == "agent_action" and event.get("identity_strength_used", 0) < event.get("strongest_identity_strength", 0):
            add("BK-04", "Action used a weaker identity despite stronger authoritative evidence")
        if event.get("type") == "message" and event.get("after_terminal", False) and not event.get("new_human_directive", False):
            add("BK-09", "Bot emitted a closure/status message after terminal state")
        if event.get("type") == "automation_run" and event.get("result") not in {
            "verified_repair", "usable_artifact", "measured_improvement", "resolved_decision",
            "completed_task", "material_alert", "silence"
        }:
            add("BK-11", "Automation produced chatter without a rent-paying outcome")
        if event.get("type") == "message" and event.get("primary_bullets", 0) > 5 and not event.get("requested_detail", False):
            add("BK-03", "Primary human surface exceeded the default five-bullet budget")
        if event.get("type") == "claim" and event.get("metric") and not event.get("metric_scope"):
            add("BK-13", "Metric claim omitted source/environment scope")
        if event.get("type") == "terminal_receipt" and event.get("scope_expanded_after_lock", False):
            add("BK-08", "Finish-line scope expanded after terminal receipt was locked")
        if event.get("type") == "owner_action_requested" and event.get("owner_unreachable", False) and not event.get("checkpoint_preserved", False):
            add("BK-10", "Owner request issued while owner unreachable without a preserved checkpoint")
        if event.get("type") == "agent_action" and event.get("high_friction_context", False) and not event.get("friction_acknowledged", False):
            add("BK-12", "High-friction context action proceeded without acknowledging the friction")

    terminal_receipts = [e for e in events if e.get("type") == "terminal_receipt"]
    successful_outcome_present = any(
        e.get("type") == "verified_outcome" and e.get("result") == "success"
        for e in events
    )
    if terminal_receipts and not successful_outcome_present:
        add(
            "BK-08",
            "Terminal receipt emitted with no successful verified_outcome event in the trace "
            "(missing, or all verified_outcome events report a non-success result)",
        )

    corrections = [e for e in events if e.get("type") == "correction"]
    preventions = {e.get("correction_id") for e in events if e.get("type") == "durable_prevention"}
    for correction in corrections:
        if correction.get("id") not in preventions:
            add("BK-14", f"Correction {correction.get('id', '<unknown>')} lacks durable prevention")

    owner_actions = sum(e.get("count", 1) for e in events if e.get("type") == "owner_action_requested")
    owner_corrections = len(corrections)
    messages = sum(1 for e in events if e.get("type") == "message")
    outcomes = sum(1 for e in events if e.get("type") == "verified_outcome")

    return {
        "trace_id": trace.get("trace_id"),
        "passed": not violations,
        "violations": violations,
        "metrics": {
            "owner_actions": owner_actions,
            "owner_corrections": owner_corrections,
            "messages": messages,
            "verified_outcomes": outcomes,
            "messages_per_verified_outcome": None if outcomes == 0 else messages / outcomes,
        },
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} TRACE.json", file=sys.stderr)
        return 2
    trace = json.loads(Path(sys.argv[1]).read_text())
    result = evaluate(trace)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
