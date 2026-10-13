# MCP Kinetic Gain aviation candidate inventory | 2026-10-13 ET

**Status: local PR-candidate review, not permission to use any tool.** The source is `mcp-kinetic-gain` PR #52 at `5a45cdcb46f86a97e05bf14faa7f6c7aa92b5545`. Its installed local tarball was started over MCP stdio; the default profile returned 75 tools and `MCP_KG_VERTICALS=aviation` returned 80. The tarball was repacked after that commit and remained byte-identical (SHA-256 `d555698804111db8cb9194093e1220f4ef0ba86f2c9fc9d2a89bf1fae06bc6a1`); the commit changed only non-packaged CI scripts/workflows. This is not a Glama build, deployed inventory, or operator decision.

The complete local `tools/list` responses were passed to `scripts/review_inventory.py`. Their input SHA-256 values were:

| Profile | Tools | Raw `tools/list` SHA-256 | Proposed classes |
| --- | ---: | --- | --- |
| Default | 75 | `37fc3f49aecbd779ed77c29e71b7c11c693b7f9a0ef8f27e4ee6bbcd26c74c9e` | Historical 75-tool map |
| Aviation opt-in | 80 | `936f889ebbe25601957de83cd29c45324cc80f567fe533564bf6dd85d1f1715d` | 48 `read-only`, 24 `approval-required`, 3 `block`, 5 `needs-evidence` |

The [candidate map](./mcp-kinetic-gain-aviation-provisional-dispositions.json) preserves every entry of the [September base map](./mcp-kinetic-gain-provisional-dispositions.json). The five additions are `aviation_ml_card_validate`, `aviation_ml_card_inspect`, `aviation_ml_card_odd_check`, `aviation_ml_card_dal_check`, and `mro_signoff_verify`. They remain `needs-evidence` **proposals** until an accountable operator reviews the actual client, environment, inputs, outputs, and permissions. The CLI returned `assessment: operator-review-required`, zero proposal/hint conflicts, and `verdict: unassessed` for all 80 tools.

The inventory analyzer now treats `readOnlyHint` as a side-effect declaration, not an authorization grant. For example, `clinical_ai_inspect` declares read-only behavior and can still perform an outbound read, so its `approval-required` proposal is not a contradiction. A `read-only` proposal still conflicts with a declared non-read-only or destructive hint. The two dimensions remain visible in the packet.

## Reproduction and limits

1. Build PR #52, pack it with `npm pack --ignore-scripts`, install the tarball in an isolated directory, and run its `dist/server.js` over MCP stdio with `MCP_KG_VERTICALS` unset and set to `aviation`.
2. Save each complete local `tools/list` JSON response outside this repository. The raw response contains descriptions and schemas, so review it before sharing.
3. Run `scripts/review_inventory.py` on each file with the exact full commit. For the opt-in profile, pass `--proposals docs/pilots/mcp-kinetic-gain-aviation-provisional-dispositions.json`.

The capture and packet contain no tool calls, buyer facts, credentials, or customer data. The installed-tarball smoke made only a synthetic local `suite_doc_detect_spec` call and an invalid aviation-card validation call. No hosted caller authentication, target-bound approval, network privacy, logs, real revocation, Glama acceptance, or rollback was verified. The three audit-service tools remain proposed `block`; this document grants no runtime enforcement and does not change the [pilot permission gate](./mcp-kinetic-gain-permission-gate-2026-10-01.md).
