from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from app.services.inventory_review import build_inventory_review


SOURCE_COMMIT = "3bb80f73dfa680e4aaf0df3032c2e01d5a919ee8"


def payload(tools: list[dict], **extra: object) -> bytes:
    return json.dumps({"tools": tools, **extra}).encode("utf-8")


def tool(name: str, annotations: dict | None = None) -> dict:
    row = {
        "name": name,
        "description": "SECRET_DO_NOT_ECHO",
        "inputSchema": {
            "type": "object",
            "properties": {"document": {"type": "string", "default": "SECRET_DO_NOT_ECHO"}},
            "required": ["document"],
        },
    }
    if annotations is not None:
        row["annotations"] = annotations
    return row


class InventoryReviewTests(unittest.TestCase):
    def test_untrusted_descriptions_and_schema_values_stay_out_of_packet(self) -> None:
        raw = payload(
            [
                tool("read_item", {"readOnlyHint": True, "destructiveHint": False}),
                tool("delete_item", {"readOnlyHint": False, "destructiveHint": True}),
            ]
        )
        packet = build_inventory_review(
            raw,
            reported_source="mcp-kinetic-gain",
            reported_commit=SOURCE_COMMIT,
            imported_at="2026-09-30T20:00:00Z",
        )
        self.assertEqual(packet["toolCount"], 2)
        self.assertEqual(packet["operatorDispositionCount"], 0)
        self.assertEqual(packet["assessment"], "operator-review-required")
        self.assertEqual(packet["tools"][0]["verdict"], "unassessed")
        self.assertEqual(packet["tools"][1]["declaredHints"]["destructive"], True)
        self.assertEqual(packet["declaredHintSummary"]["readOnlyTrue"], 1)
        self.assertEqual(packet["declaredHintSummary"]["destructiveTrue"], 1)
        self.assertEqual(packet["declaredAttentionToolNames"], ["delete_item"])
        self.assertEqual(packet["missingReadOnlyToolNames"], [])
        self.assertNotIn("SECRET_DO_NOT_ECHO", json.dumps(packet))

    def test_operator_disagreement_is_reported_without_claiming_a_pass(self) -> None:
        packet = build_inventory_review(
            payload(
                [
                    tool("read_item", {"readOnlyHint": True, "destructiveHint": False}),
                    tool("mutating_item", {"readOnlyHint": False}),
                    tool("unknown_item"),
                ]
            ),
            reported_source="mcp-kinetic-gain",
            reported_commit=SOURCE_COMMIT,
            imported_at="2026-09-30T20:00:00Z",
            decisions={"read_item": "block", "mutating_item": "read-only"},
        )
        self.assertEqual(packet["operatorDispositionCount"], 2)
        self.assertEqual(packet["declarationDisagreements"], ["read_item", "mutating_item"])
        self.assertEqual(packet["missingReadOnlyToolNames"], ["unknown_item"])
        self.assertEqual(packet["tools"][0]["verdict"], "unassessed")

    def test_partial_or_malformed_inventory_fails_closed(self) -> None:
        cases = [
            payload([tool("one")], nextCursor="next-page"),
            payload([tool("one")], nextCursor=""),
            payload([tool("one"), tool("one")]),
            payload([tool("one", {"readOnlyHint": "true"})]),
            payload([{"name": "one", "inputSchema": {"type": "string"}}]),
            payload([]),
            b'{"tools":[{"name":"one","inputSchema":{"type":"object"},"annotations":{"readOnlyHint":true,"readOnlyHint":false}}]}',
            b'{"tools":[{"name":"one","inputSchema":{"type":"object"},"annotations":{"readOnlyHint":NaN}}]}',
        ]
        for raw in cases:
            with self.subTest(raw=raw[:50]), self.assertRaises(ValueError):
                build_inventory_review(raw, "mcp-kinetic-gain", SOURCE_COMMIT)

    def test_unknown_operator_decision_is_rejected(self) -> None:
        for decisions in ({"other": "read-only"}, {"one": ["read-only"]}):
            with self.subTest(decisions=decisions), self.assertRaises(ValueError):
                build_inventory_review(
                    payload([tool("one")]),
                    "mcp-kinetic-gain",
                    SOURCE_COMMIT,
                    decisions=decisions,
                )

    def test_cli_error_does_not_echo_inventory_content(self) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts" / "review_inventory.py"
        with tempfile.TemporaryDirectory() as directory:
            inventory = Path(directory) / "inventory.json"
            inventory.write_text('{"tools": ["SECRET_DO_NOT_ECHO"]}', encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(inventory),
                    "--source",
                    "mcp-kinetic-gain",
                    "--commit",
                    SOURCE_COMMIT,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("SECRET_DO_NOT_ECHO", result.stderr)


if __name__ == "__main__":
    unittest.main()
