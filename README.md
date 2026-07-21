# sovereign-agent-network

Open collaboration layer for sovereign personal agents, shared corpuses, Personal OS primitives, Work Kernel, and agent reliability.

## Shared bootstrap protocols

- [Owner-First Authentication and Secret Handoff](bootstrap/OWNER_FIRST_AUTH_HANDOFF.md): agents perform setup, secret-store plumbing, and verification; owners handle only irreducible human gates through direct exact-gate links.
- Machine-readable contract: [`bootstrap/owner-first-auth-handoff.json`](bootstrap/owner-first-auth-handoff.json)
- Validation: `python bootstrap/validate_owner_first_auth_handoff.py`
- Tests: `pytest -q bootstrap/test_owner_first_auth_handoff.py`
