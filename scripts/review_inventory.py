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
    parser.add_argument("--proposals", type=Path, help="Optional local tool-name to proposed-disposition JSON map; never authorization")
    args = parser.parse_args()
    try:
        with args.inventory.open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        proposals = None
        if args.proposals is not None:
            with args.proposals.open("rb") as handle:
                proposal_bytes = handle.read(MAX_INPUT_BYTES + 1)
            if len(proposal_bytes) > MAX_INPUT_BYTES:
                raise ValueError("Proposal file is too large")
            proposals = parse_strict_json(proposal_bytes)
        packet = build_inventory_review(raw, args.source, args.commit, proposals=proposals)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # Avoid echoing caller-supplied text, paths, descriptions or schema values.
        print(f"Inventory review failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    json.dump(packet, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
