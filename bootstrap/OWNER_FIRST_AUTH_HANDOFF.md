# Owner-First Authentication and Secret Handoff

## Purpose

A capable personal agent removes setup work from its owner. The owner should never be turned into the agent's DevOps operator merely because authentication, a password manager, or a secret is involved.

## Required operating rule

For every account, API, connector, repository, password manager, or server bootstrap:

1. **Agent does the setup work first.** Discover the live environment, install or configure reversible prerequisites, open the correct provider page, and drive the flow to the exact human gate.
2. **Use an approved secret store.** Prefer the owner's existing password manager. If none exists, help establish one and a separate agent-accessible secret boundary. Never put passwords, tokens, recovery codes, private keys, cookies, or device codes in Discord, commits, logs, or shared brain pages.
3. **Send direct access, not instructions.** If owner action is unavoidable, initiate the invitation, secure collection form, persistent-browser session, or provider consent flow and send the owner a direct link already positioned at the exact gate. Do not tell the owner to find a terminal, SSH into a VPS, browse settings, copy commands, or hunt for links when the agent can do it.
4. **Owner performs only irreducible human gates.** Valid gates include CAPTCHA, passkey, MFA/device approval, explicit provider consent, identity verification, payment approval, or a password-manager invitation that only the owner can accept.
5. **Agent resumes automatically.** Keep the browser, OAuth waiter, callback listener, or setup process alive. Detect completion when possible, finish the downstream setup, store credentials, and run a real smoke test.
6. **No security theater.** Security should remove recurring owner work, not add it. Use least necessary scope, revocable access, separate agent credentials where supported, secret-safe logs, and a tested recovery path.
7. **Do not over-escalate.** Before reporting a blocker, try saved credentials, existing authenticated sessions, official API/OAuth paths, email or magic-link recovery available to the agent, managed browser automation, and one safe alternate route.

## Password-manager bootstrap

The agent must:

- detect whether the owner already uses 1Password, Bitwarden, or another approved manager;
- verify agent-side access without exposing secret values;
- if access is absent, create or prepare the narrowest appropriate organization, collection, vault, service account, or machine credential supported by the chosen manager;
- initiate the exact invitation or enrollment flow;
- send the owner the direct invitation or secure handoff link;
- store agent credentials only in the approved agent boundary;
- verify one secret can be retrieved at runtime without printing it;
- record only secret-free metadata: manager, vault or collection name, credential type, scope, recovery owner, verification time, and revocation path.

## Acceptance test

A bootstrap passes only when all are true:

- The owner received at most the irreducible human gate, not terminal or navigation work.
- No secret appeared in Discord, repository history, logs, or shared artifacts.
- The agent can retrieve the credential from the approved store at runtime.
- One real authenticated capability was exercised successfully.
- The access is scoped, revocable, and recoverable by the owner.
- The bootstrap receipt distinguishes `prepared`, `human_gate_waiting`, `authenticated`, and `live_verified`.

## Failure examples

- Telling the owner to open a VPS console and run commands when the agent can operate the server or browser.
- Asking for a password, token, or device code in a shared Discord channel.
- Sending a generic login page rather than a live exact-gate link.
- Declaring completion because a password manager was installed, without proving runtime retrieval and real use.
- Repeatedly triggering MFA or CAPTCHA instead of preserving one controlled setup session.
