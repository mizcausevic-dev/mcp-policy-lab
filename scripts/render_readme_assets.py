from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.policy_service import build_service


OUT_DIR = ROOT / "screenshots"
OUT_DIR.mkdir(exist_ok=True)


def write_svg(filename: str, title: str, subtitle: str, lines: list[str]) -> None:
    rows = "\n".join(
        f"<text x='52' y='{220 + index * 44}' fill='#d9e6ff' font-size='22' font-family='Segoe UI'>{line}</text>"
        for index, line in enumerate(lines)
    )
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='900' viewBox='0 0 1440 900'>
  <defs>
    <linearGradient id='bg' x1='0' x2='1' y1='0' y2='1'>
      <stop offset='0%' stop-color='#07101b'/>
      <stop offset='100%' stop-color='#0f2240'/>
    </linearGradient>
  </defs>
  <rect width='1440' height='900' fill='url(#bg)'/>
  <rect x='38' y='36' width='1364' height='828' rx='24' fill='#0b1728' stroke='#1f3e62'/>
  <text x='52' y='98' fill='#73b7ff' font-size='18' letter-spacing='4' font-family='Segoe UI'>MCP POLICY LAB</text>
  <text x='52' y='166' fill='#f5f9ff' font-size='54' font-weight='700' font-family='Georgia, Segoe UI'>{title}</text>
  <text x='52' y='198' fill='#9eb3cf' font-size='24' font-family='Segoe UI'>{subtitle}</text>
  {rows}
</svg>"""
    (OUT_DIR / filename).write_text(svg, encoding="utf-8")


def main() -> None:
    service = build_service()
    summary = service.summary()
    queue = service.policy_queue()
    matrix = service.tool_matrix()
    sample = json.dumps(service.sample_payload(), indent=2).splitlines()[:7]

    write_svg(
        "01-overview.svg",
        "Control-plane summary for MCP trust posture.",
        "Server count, critical lanes, and operator recommendations at a glance.",
        [
            f"Servers under policy review: {summary['serverCount']}",
            f"Critical containment lanes: {summary['criticalServers']}",
            f"Average risk score: {summary['averageRiskScore']}",
            f"Lead recommendation: {summary['leadRecommendation']}",
        ],
    )
    write_svg(
        "02-policy-queue.svg",
        "Review queue for destructive-action exposure.",
        "The servers most likely to need containment or human review.",
        [
            f"{item['name']} | {item['verdict']} | risk {item['riskScore']} | {item['policyGap']}"
            for item in queue[:4]
        ],
    )
    write_svg(
        "03-tool-matrix.svg",
        "Tool matrix for schema and evidence posture.",
        "High-risk tools stay visible even when the server surface looks healthy.",
        [
            f"{item['toolName']} | {item['riskClass']} | schema {item['schemaCoverage']}% | evidence {item['evidenceCoverage']}%"
            for item in matrix[:4]
        ],
    )
    write_svg(
        "04-api-summary.svg",
        "API sample for CI and governance workflows.",
        "The same policy outputs can feed review queues, CI gates, or broader MCP platforms.",
        [line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for line in sample],
    )
    print("rendered screenshots")


if __name__ == "__main__":
    main()
