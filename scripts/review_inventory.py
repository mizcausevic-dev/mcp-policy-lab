"""Render a local review packet from a complete MCP tools/list JSON response."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.inventory_review import MAX_INPUT_BYTES, build_inventory_review, parse_strict_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path, help="Complete, local tools/list JSON file")
    parser.add_argument("--source", required=True, help="Reported source label, not an attestation")
    parser.add_argument("--commit", required=True, help="Reported full source commit SHA")
    parser.add_argument("--decisions", type=Path, help="Optional local tool-name to operator-decision JSON map")
    args = parser.parse_args()
    try:
        with args.inventory.open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        decisions = None
        if args.decisions is not None:
            with args.decisions.open("rb") as handle:
                decision_bytes = handle.read(MAX_INPUT_BYTES + 1)
            if len(decision_bytes) > MAX_INPUT_BYTES:
                raise ValueError("Decision file is too large")
            decisions = parse_strict_json(decision_bytes)
        packet = build_inventory_review(raw, args.source, args.commit, decisions=decisions)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # Avoid echoing caller-supplied text, paths, descriptions or schema values.
        print(f"Inventory review failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    json.dump(packet, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
