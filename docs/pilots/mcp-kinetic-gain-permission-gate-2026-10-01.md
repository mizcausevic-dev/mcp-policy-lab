# MCP Kinetic Gain pilot permission gate

**Status: BLOCKED for a connected or production pilot.** The 75-tool inventory and [provisional dispositions](./mcp-kinetic-gain-provisional-dispositions.json) are an engineering review of a local `tools/list` capture. They grant no client access. The Policy Lab web service remains a synthetic fixture and never calls `mcp-kinetic-gain`.

## What is already bounded

- Inventory provenance is reported as source commit `3bb80f73dfa680e4aaf0df3032c2e01d5a919ee8` and raw-capture SHA-256 `ac05facc55af360e8cd8c4bbadcb5d6a72c2b73cfec9112847fba9853fe09996`. These values identify the reviewed input; they do not attest to a deployed binary or client configuration.
- The static map has 48 local read-only **candidates**, 24 network-capable tools proposed for per-call approval, and three audit-service tools proposed to stay blocked. The CLI reports these as `proposedDisposition` and leaves every `verdict` `unassessed`.
- The documented `python -m app.main` local run binds to `127.0.0.1`, uses bundled sample data, and has no connector or runtime permission enforcement. This is a local review aid, not a policy decision point.

## Operator decisions and proof still required

An accountable owner of the **actual MCP deployment** must provide a review record, kept outside this public repository, for each client and environment. Record the client identity, authenticated principal, token audience and scopes, the exact allowed tool names, resource or target allowlist, who can approve an external read, approval lifetime, and evidence/retention owner. Do not put tokens, customer data, or approval screenshots containing sensitive information into this repository.

The connected pilot cannot start until the deployed MCP boundary is shown to enforce these decisions. The proof must include:

1. A client with no grant sees or can invoke no pilot tools. A permitted test client sees only its approved subset; a direct call to a hidden or denied name fails. A prompt or tool result cannot broaden that subset.
2. A local read-only candidate is tested with authorized, non-sensitive inputs for output disclosure, memory mutation, file writes, and network calls. Source inspection alone is insufficient.
3. Each of the 24 network-capable tools has a caller-and-target-bound consent path, target URL allowlist, redirect/DNS/egress checks, bounded timeout, and redacted failure log. No broad approval for an arbitrary `url` argument.
4. `audit_event_emit`, `audit_events_query`, and `audit_chain_verify_live` remain unavailable. To change that, separately prove audit-service identity, caller/resource and tenant authorization, event privacy, retention, and recovery. The POST additionally needs idempotency and a controlled write rollback.
5. Test denied, expired, wrong-audience, wrong-resource, cross-tenant, and revoked access at the deployed boundary; retain redacted request IDs and results. Verify that a rollback restores the prior permission set without exposing the blocked tools.

Until those checks run with the actual operator and environment, the only safe permission posture documented here is **deny all connected tool access**. A proposed map or a structurally complete approval form cannot substitute for observed enforcement.
