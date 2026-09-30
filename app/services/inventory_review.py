"""Local, read-only review packet for one complete MCP tools/list response.

Tool annotations are declarations from the server, not verified controls. This
module deliberately does not feed incomplete inventory data into the sample
server posture score or copy descriptions and schema values into its output.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone


MAX_INPUT_BYTES = 2_000_000
MAX_TOOLS = 1_000
NAME = re.compile(r"^[A-Za-z0-9_.:/-]{1,128}$")
SOURCE = re.compile(r"^[A-Za-z0-9_.:/@-]{1,200}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DECISIONS = {"read-only", "approval-required", "block", "needs-evidence"}
HINTS = {
    "readOnlyHint": "readOnly",
    "destructiveHint": "destructive",
    "idempotentHint": "idempotent",
    "openWorldHint": "openWorld",
}


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains duplicate keys")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("JSON contains a nonfinite value")


def parse_strict_json(raw: bytes) -> object:
    return json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)


def build_inventory_review(
    raw: bytes,
    reported_source: str,
    reported_commit: str,
    *,
    decisions: dict[str, str] | None = None,
    imported_at: str | None = None,
) -> dict:
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_INPUT_BYTES:
        raise ValueError("Inventory file must be nonempty and at most 2 MB")
    if (
        not isinstance(reported_source, str)
        or not isinstance(reported_commit, str)
        or not SOURCE.fullmatch(reported_source)
        or not COMMIT.fullmatch(reported_commit)
    ):
        raise ValueError("Invalid reported source or full commit SHA")
    try:
        payload = parse_strict_json(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Inventory is not valid JSON") from exc
    if not isinstance(payload, dict) or payload.get("nextCursor") is not None:
        raise ValueError("Expected one complete tools/list response")
    tools = payload.get("tools")
    if not isinstance(tools, list) or not 0 < len(tools) <= MAX_TOOLS:
        raise ValueError("Inventory must contain 1 to 1000 tools")

    decisions = {} if decisions is None else decisions
    if not isinstance(decisions, dict) or any(
        not isinstance(name, str) or not isinstance(decision, str) or decision not in DECISIONS
        for name, decision in decisions.items()
    ):
        raise ValueError("Operator decisions have an invalid shape or value")

    rows: list[dict] = []
    seen: set[str] = set()
    disagreements: list[str] = []
    annotation_conflicts: list[str] = []
    declared_attention_tools: list[str] = []
    missing_read_only_tools: list[str] = []
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict):
            raise ValueError(f"Tool {index} is not an object")
        name = tool.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name) or name in seen:
            raise ValueError(f"Tool {index} has an invalid or duplicate name")
        seen.add(name)
        schema = tool.get("inputSchema")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            raise ValueError(f"Tool {index} lacks an object input schema")
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list) or any(
            not isinstance(item, str) for item in required
        ):
            raise ValueError(f"Tool {index} has an invalid input schema shape")
        annotations = tool.get("annotations", {})
        if not isinstance(annotations, dict):
            raise ValueError(f"Tool {index} has invalid annotations")
        declared: dict[str, bool | None] = {}
        for source_key, output_key in HINTS.items():
            hint = annotations.get(source_key)
            if hint is not None and not isinstance(hint, bool):
                raise ValueError(f"Tool {index} has a non-boolean annotation hint")
            declared[output_key] = hint

        decision = decisions.get(name)
        if declared["readOnly"] is True and declared["destructive"] is True:
            annotation_conflicts.append(name)
        if (
            declared["readOnly"] is False
            or declared["destructive"] is True
            or declared["openWorld"] is True
        ):
            declared_attention_tools.append(name)
        if declared["readOnly"] is None:
            missing_read_only_tools.append(name)
        if decision in ("approval-required", "block") and declared["readOnly"] is True:
            disagreements.append(name)
        elif decision == "read-only" and (
            declared["destructive"] is True or declared["readOnly"] is False
        ):
            disagreements.append(name)
        rows.append(
            {
                "name": name,
                "declaredHints": declared,
                "schemaPropertyCount": len(properties),
                "schemaRequiredCount": len(required),
                "operatorDecision": decision,
                "verdict": "unassessed",
            }
        )

    if decisions.keys() - seen:
        raise ValueError("Operator decision refers to a tool outside the inventory")
    timestamp = imported_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise ValueError("Import time must be a UTC timestamp")
    return {
        "reportedSource": reported_source,
        "reportedSourceCommit": reported_commit,
        "importedAt": timestamp,
        "inputSha256": hashlib.sha256(raw).hexdigest(),
        "assessment": "operator-review-required",
        "toolCount": len(rows),
        "operatorDispositionCount": len(decisions),
        "withoutOperatorDispositionCount": len(rows) - len(decisions),
        "declarationDisagreements": disagreements,
        "annotationConflicts": annotation_conflicts,
        "declaredHintSummary": {
            "readOnlyTrue": sum(row["declaredHints"]["readOnly"] is True for row in rows),
            "readOnlyFalse": sum(row["declaredHints"]["readOnly"] is False for row in rows),
            "readOnlyUnknown": sum(row["declaredHints"]["readOnly"] is None for row in rows),
            "destructiveTrue": sum(row["declaredHints"]["destructive"] is True for row in rows),
            "openWorldTrue": sum(row["declaredHints"]["openWorld"] is True for row in rows),
        },
        "declaredAttentionToolNames": declared_attention_tools,
        "missingReadOnlyToolNames": missing_read_only_tools,
        "tools": rows,
    }
