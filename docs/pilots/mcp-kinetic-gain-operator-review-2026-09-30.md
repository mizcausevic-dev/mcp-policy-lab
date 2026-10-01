# MCP Kinetic Gain inventory review, 2026-09-30 ET

**Status: provisional engineering dispositions, not operator authorization.** This is a static source review of `mcp-kinetic-gain` commit `3bb80f73dfa680e4aaf0df3032c2e01d5a919ee8` and a local MCP stdio `tools/list` capture with SHA-256 `ac05facc55af360e8cd8c4bbadcb5d6a72c2b73cfec9112847fba9853fe09996`. GitHub `main` and the clean local checkout matched that commit when reviewed. No tool was called to create this inventory. The original raw capture, which includes descriptions and schemas, stays outside this repository.

The [disposition map](./mcp-kinetic-gain-provisional-dispositions.json) lists all 75 tool names. It records **48 `read-only` candidates**, **24 `approval-required` candidates**, and **three `block` candidates**. These labels describe the operation class inferred from handler source. They do not prove caller authorization, result privacy, complete side-effect absence, or policy enforcement. When imported through `scripts/review_inventory.py`, all 75 verdicts remain `unassessed`.

| Operation class | Disposition | Source basis | Remaining gate |
| --- | --- | --- | --- |
| 48 local parse, validate, hash, derive, or URL-construction tools | `read-only` | `src/server.ts` handler mapping and static scan of `src/handlers/`; no persistent write or network call found in these handlers. `claims_card_chain` mutates its input object in process while constructing a result. | Review with authorized, non-sensitive inputs; verify output disclosure and runtime side effects before granting client access. |
| 20 handlers accepting `url`, plus `aeo_fetch`, `aeo_inspect`, `aeo_get_claim`, and `incident_index_fetch` | `approval-required` | Their handlers can call `fetchJson` in `src/common.ts`, which performs outbound GETs. Some `url` tools can instead process pasted JSON; the exposed tool remains network-capable. | Bind consent to caller and target; test egress policy, redirect/DNS guard, returned data, and error logging against the actual deployment. |
| `audit_events_query` and `audit_chain_verify_live` | `block` | `src/handlers/audit-stream-live.ts` GETs a service named by `AUDIT_STREAM_URL`; the source review did not verify that service's identity, authorization, tenant boundary, or returned event privacy. | Keep disabled until those boundaries and network policy are proven. |
| `audit_event_emit` | `block` | The same handler POSTs a persistent event to `AUDIT_STREAM_URL`. It is the one tool declaring `readOnlyHint: false` and `openWorldHint: true`. | Keep disabled until the target, caller/resource authorization, consent, idempotency, audit retention, and rollback/recovery are proven. |

The other 74 tools have no `readOnlyHint` in the captured descriptor. Missing annotations are still reported separately; this review does not fill them in or convert declarations into proof. The disposition map has zero direct disagreements with the one explicit hint, but that does not validate any classification.

## Checks and limits

- Source `npm.cmd test -- tests/url-guard.test.ts tests/audit-stream-live.test.ts tests/claims-card.test.ts`: 36/36 passed across three files.
- Source `npm.cmd run typecheck`: exit 0.
- The Policy Lab CLI accepted the complete capture plus the disposition map, counted 75 dispositions (48/24/3), and kept 75 verdicts `unassessed`. The local packet and generator live with the capture outside this repository.
- This review did **not** call any tool, test a real audit-stream service, inspect a deployed network boundary, use customer data, or verify production rollback. Source tests and static inspection cannot prove those boundaries.

Before operational use, an accountable operator must confirm these provisional labels against the deployed identities, target URLs, permissions, and side effects. The three `block` dispositions must remain in force unless a separate controlled release proves their service boundary and the write path where applicable.
