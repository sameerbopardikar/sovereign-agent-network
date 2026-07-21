# sovereign-agent-network

Open collaboration layer for sovereign personal agents, shared corpuses, Personal OS primitives, Work Kernel, and agent reliability.

## Shared protocols

### Owner-first authentication

- [Owner-First Authentication and Secret Handoff](bootstrap/OWNER_FIRST_AUTH_HANDOFF.md): agents perform setup, secret-store plumbing, and verification; owners handle only irreducible human gates through direct exact-gate links.
- Machine-readable contract: [`bootstrap/owner-first-auth-handoff.json`](bootstrap/owner-first-auth-handoff.json)
- Validation: `python bootstrap/validate_owner_first_auth_handoff.py`
- Tests: `pytest -q bootstrap/test_owner_first_auth_handoff.py`

### Behavioral Kernel

- [Sovereign Agent Behavioral Kernel](behavior/BEHAVIORAL_KERNEL.md): observable owner-first behavior, claim maturity, terminal silence, fallback discipline, reachability, and automation-value rules.
- Machine-readable contract: [`behavior/behavioral-kernel.json`](behavior/behavioral-kernel.json)
- Trace evaluator: `python behavior/evaluate_behavioral_trace.py TRACE.json`
- Scenario tests: `pytest -q behavior/test_behavioral_kernel.py`
