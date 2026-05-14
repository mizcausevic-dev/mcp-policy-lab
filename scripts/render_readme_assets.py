from __future__ import annotations

import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.policy_service import build_service


OUT_DIR = ROOT / "screenshots"
OUT_DIR.mkdir(exist_ok=True)

WIDTH = 1600
HEIGHT = 980


def shell(title: str, subtitle: str, body: str) -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' viewBox='0 0 {WIDTH} {HEIGHT}'>
  <defs>
    <linearGradient id='bg' x1='0' x2='0' y1='0' y2='1'>
      <stop offset='0%' stop-color='#02050b'/>
      <stop offset='100%' stop-color='#07101b'/>
    </linearGradient>
    <linearGradient id='hero' x1='0' x2='1' y1='0' y2='1'>
      <stop offset='0%' stop-color='#0a1221'/>
      <stop offset='100%' stop-color='#08111d'/>
    </linearGradient>
    <linearGradient id='blue' x1='0' x2='1' y1='0' y2='0'>
      <stop offset='0%' stop-color='#0d94c8'/>
      <stop offset='100%' stop-color='#3978ff'/>
    </linearGradient>
    <linearGradient id='good' x1='0' x2='1' y1='0' y2='0'>
      <stop offset='0%' stop-color='#1f8bd1'/>
      <stop offset='100%' stop-color='#44d39d'/>
    </linearGradient>
    <linearGradient id='watch' x1='0' x2='1' y1='0' y2='0'>
      <stop offset='0%' stop-color='#2f82ff'/>
      <stop offset='100%' stop-color='#f4c76d'/>
    </linearGradient>
    <linearGradient id='hot' x1='0' x2='1' y1='0' y2='0'>
      <stop offset='0%' stop-color='#d14d6c'/>
      <stop offset='100%' stop-color='#ff7a88'/>
    </linearGradient>
  </defs>
  <rect width='{WIDTH}' height='{HEIGHT}' fill='url(#bg)'/>
  <rect x='0' y='0' width='260' height='{HEIGHT}' fill='rgba(0,0,0,0.32)'/>
  <rect x='0' y='0' width='260' height='{HEIGHT}' fill='none' stroke='rgba(255,255,255,0.06)'/>
  <rect x='22' y='26' width='216' height='64' rx='20' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.08)'/>
  <rect x='36' y='38' width='40' height='40' rx='12' fill='url(#blue)'/>
  <text x='56' y='63' text-anchor='middle' fill='#ffffff' font-size='16' font-family='Segoe UI' font-weight='700'>PL</text>
  <text x='90' y='58' fill='#f6f8fe' font-size='15' font-family='Segoe UI' font-weight='700'>MCP Policy Lab</text>
  <text x='90' y='76' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>INSTANCE: POL-ALPHA</text>
  <text x='36' y='142' fill='#6ec5ff' font-size='11' font-family='Segoe UI' letter-spacing='4'>ACTIVE VIEWS</text>
  <rect x='26' y='164' width='208' height='42' rx='14' fill='rgba(110,197,255,0.08)' stroke='rgba(110,197,255,0.16)'/>
  <text x='42' y='190' fill='#6ec5ff' font-size='12' font-family='Segoe UI' letter-spacing='2'>OVERVIEW</text>
  <text x='42' y='236' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>POLICY QUEUE</text>
  <text x='42' y='282' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>TOOL MATRIX</text>
  <text x='42' y='328' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>AUDIT METHODOLOGY</text>
  <rect x='260' y='0' width='{WIDTH - 260}' height='72' fill='rgba(0,0,0,0.32)'/>
  <rect x='260' y='72' width='{WIDTH - 260}' height='1' fill='rgba(255,255,255,0.08)'/>
  <rect x='294' y='20' width='184' height='30' rx='15' fill='rgba(110,197,255,0.05)' stroke='rgba(110,197,255,0.14)'/>
  <circle cx='314' cy='35' r='5' fill='#6ec5ff'/>
  <text x='330' y='39' fill='#a8d8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>SAFETY FEED ACTIVE</text>
  <rect x='1290' y='16' width='250' height='38' rx='19' fill='url(#blue)'/>
  <text x='1415' y='39' fill='#ffffff' text-anchor='middle' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>OPEN API DOCS</text>
  <rect x='294' y='104' width='1240' height='248' rx='28' fill='url(#hero)' stroke='rgba(120,163,214,0.18)'/>
  <text x='332' y='146' fill='#6ec5ff' font-size='11' font-family='Segoe UI' letter-spacing='5'>MCP POLICY LAB</text>
  <text x='332' y='212' fill='#f6f8fe' font-size='44' font-family='Georgia' font-weight='700'>{escape(title)}</text>
  <text x='332' y='248' fill='#93a7c5' font-size='21' font-family='Segoe UI'>{escape(subtitle)}</text>
  {body}
</svg>"""


def stat_card(x: int, y: int, label: str, value: str, sub: str) -> str:
    return f"""
  <rect x='{x}' y='{y}' width='280' height='132' rx='20' fill='rgba(255,255,255,0.04)' stroke='rgba(255,255,255,0.06)'/>
  <text x='{x + 22}' y='{y + 28}' fill='#71839d' font-size='10' font-family='Segoe UI' letter-spacing='3'>{escape(label.upper())}</text>
  <text x='{x + 22}' y='{y + 72}' fill='#f6f8fe' font-size='38' font-family='Segoe UI' font-weight='700'>{escape(value)}</text>
  <text x='{x + 22}' y='{y + 102}' fill='#93a7c5' font-size='14' font-family='Segoe UI'>{escape(sub)}</text>
    """


def meter(x: int, y: int, label: str, value: float, tone: str) -> str:
    width = int(260 * max(0, min(100, value)) / 100)
    gradient = {"good": "good", "watch": "watch", "hot": "hot"}[tone]
    return f"""
  <text x='{x}' y='{y}' fill='#cfe0f7' font-size='12' font-family='Segoe UI'>{escape(label)}</text>
  <text x='{x + 250}' y='{y}' text-anchor='end' fill='#cfe0f7' font-size='12' font-family='Segoe UI' font-weight='700'>{round(value)}%</text>
  <rect x='{x}' y='{y + 12}' width='260' height='10' rx='5' fill='rgba(255,255,255,0.06)'/>
  <rect x='{x}' y='{y + 12}' width='{width}' height='10' rx='5' fill='url(#{gradient})'/>
    """


def overview_svg() -> str:
    service = build_service()
    summary = service.summary()
    catalog = service.server_catalog()
    body = [
        stat_card(332, 274, "Servers under review", str(summary["serverCount"]), "Policy-evaluated MCP servers across current lanes."),
        stat_card(628, 274, "Containment lanes", str(summary["criticalServers"]), "Servers that should not expand trust yet."),
        stat_card(924, 274, "Average risk score", str(summary["averageRiskScore"]), "Cross-surface posture based on tools and controls."),
        stat_card(1220, 274, "Tool inventory", str(summary["toolCount"]), "Tools scored for approval, schema, and evidence."),
        f"""
  <rect x='332' y='380' width='1240' height='94' rx='20' fill='rgba(2,8,17,0.62)' stroke='rgba(255,255,255,0.06)'/>
  <text x='356' y='410' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>LEAD RECOMMENDATION</text>
  <text x='356' y='446' fill='#d7e5fb' font-size='18' font-family='Segoe UI'>{escape(summary["leadRecommendation"])}</text>
  <rect x='332' y='500' width='410' height='388' rx='22' fill='rgba(4,9,18,0.55)' stroke='rgba(255,255,255,0.06)'/>
  <text x='356' y='534' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>Average trust metrics</text>
  {meter(356, 578, 'Auth model strength', 76, 'watch')}
  {meter(356, 640, 'Network zoning', 71, 'watch')}
  {meter(356, 702, 'Approval hygiene', 75, 'watch')}
  {meter(356, 764, 'Evidence retention', summary['averageEvidenceCoverage'], 'good')}
  <rect x='770' y='500' width='802' height='388' rx='22' fill='rgba(4,9,18,0.55)' stroke='rgba(255,255,255,0.06)'/>
  <text x='794' y='534' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>Server posture board</text>
        """,
    ]
    card_y = 570
    for index, item in enumerate(catalog[:3]):
        y = card_y + index * 102
        verdict_fill = {"stable": "#44d39d", "review": "#f4c76d", "contain": "#ff7a88"}[item["verdict"]]
        body.append(
            f"""
  <rect x='794' y='{y}' width='754' height='84' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='820' y='{y + 30}' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>{escape(item["name"])}</text>
  <text x='820' y='{y + 52}' fill='#93a7c5' font-size='12' font-family='Segoe UI'>{escape(item["owner"])} · {escape(item["environment"])} · {escape(item["authModel"])}</text>
  <rect x='1210' y='{y + 18}' width='104' height='28' rx='14' fill='rgba(255,255,255,0.04)' stroke='rgba(255,255,255,0.06)'/>
  <text x='1262' y='{y + 37}' text-anchor='middle' fill='{verdict_fill}' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(item["verdict"].upper())}</text>
  <text x='1380' y='{y + 32}' fill='#6f83a0' font-size='10' font-family='Segoe UI' letter-spacing='2'>RISK SCORE</text>
  <text x='1516' y='{y + 36}' text-anchor='end' fill='#f6f8fe' font-size='28' font-family='Segoe UI' font-weight='700'>{item["riskScore"]}</text>
  <text x='820' y='{y + 72}' fill='#cfe0f7' font-size='12' font-family='Segoe UI'>Schema {item["schemaCoverage"]}% · Evidence {item["evidenceCoverage"]}% · {escape(item["nextAction"][:70])}...</text>
            """
        )
    return shell("Control-plane summary for MCP trust posture.", "Server count, critical lanes, and operator recommendations at a glance.", "".join(body))


def policy_queue_svg() -> str:
    queue = build_service().policy_queue()
    body = [
        """
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>REVIEW QUEUE</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>Review queue for destructive-action exposure.</text>
  <text x='356' y='492' fill='#93a7c5' font-size='15' font-family='Segoe UI'>The servers most likely to need containment or human review.</text>
        """
    ]
    for index, item in enumerate(queue):
        y = 530 + index * 122
        verdict_fill = {"review": "#f4c76d", "contain": "#ff7a88"}[item["verdict"]]
        body.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='98' rx='18' fill='rgba(4,9,18,0.58)' stroke='rgba(255,255,255,0.05)'/>
  <text x='384' y='{y + 32}' fill='#f6f8fe' font-size='22' font-family='Segoe UI' font-weight='700'>{escape(item["name"])}</text>
  <text x='384' y='{y + 54}' fill='#93a7c5' font-size='12' font-family='Segoe UI'>{escape(item["owner"])}</text>
  <rect x='1112' y='{y + 18}' width='104' height='28' rx='14' fill='rgba(255,255,255,0.04)' stroke='rgba(255,255,255,0.06)'/>
  <text x='1164' y='{y + 37}' text-anchor='middle' fill='{verdict_fill}' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(item["verdict"].upper())}</text>
  <text x='1296' y='{y + 30}' fill='#6f83a0' font-size='10' font-family='Segoe UI' letter-spacing='2'>RISK SCORE</text>
  <text x='1508' y='{y + 36}' text-anchor='end' fill='#f6f8fe' font-size='28' font-family='Segoe UI' font-weight='700'>{item["riskScore"]}</text>
  <text x='384' y='{y + 80}' fill='#cfe0f7' font-size='13' font-family='Segoe UI'>{escape(item["policyGap"])}</text>
            """
        )
    return shell("Review queue for destructive-action exposure.", "The servers most likely to need containment or human review.", "".join(body))


def tool_matrix_svg() -> str:
    matrix = build_service().tool_matrix()
    rows = []
    y = 560
    for item in matrix[:6]:
        tone = {"low": "#b7c7de", "medium": "#6ec5ff", "high": "#f4c76d", "critical": "#ff7a88"}[item["riskClass"]]
        rows.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='54' fill='{"rgba(255,255,255,0.02)" if (y // 54) % 2 else "rgba(0,0,0,0.06)"}'/>
  <text x='382' y='{y + 22}' fill='#f6f8fe' font-size='14' font-family='Segoe UI' font-weight='700'>{escape(item["toolName"])}</text>
  <text x='382' y='{y + 40}' fill='#93a7c5' font-size='11' font-family='Segoe UI'>{escape(item["serverName"])}</text>
  <text x='880' y='{y + 32}' fill='{tone}' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(item["riskClass"].upper())}</text>
  <text x='1040' y='{y + 32}' fill='{"#44d39d" if item["destructive"] else "#93a7c5"}' font-size='12' font-family='Segoe UI'>{'Yes' if item["destructive"] else 'No'}</text>
  <text x='1168' y='{y + 32}' fill='{"#44d39d" if item["requiresApproval"] else "#ff7a88"}' font-size='12' font-family='Segoe UI'>{'Yes' if item["requiresApproval"] else 'No'}</text>
  <text x='1312' y='{y + 32}' fill='#f6f8fe' font-size='12' font-family='Segoe UI'>{item["schemaCoverage"]}%</text>
  <text x='1456' y='{y + 32}' fill='#f6f8fe' font-size='12' font-family='Segoe UI'>{item["evidenceCoverage"]}%</text>
            """
        )
        y += 54
    body = f"""
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>TOOL INVENTORY</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>Tool matrix for schema and evidence posture.</text>
  <text x='356' y='492' fill='#93a7c5' font-size='15' font-family='Segoe UI'>High-risk tools stay visible even when the server surface looks healthy.</text>
  <rect x='356' y='520' width='1192' height='46' fill='rgba(255,255,255,0.04)'/>
  <text x='382' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>TOOL IDENTITY</text>
  <text x='880' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>RISK</text>
  <text x='1030' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>DESTRUCTIVE</text>
  <text x='1150' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>APPROVAL</text>
  <text x='1298' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>SCHEMA</text>
  <text x='1438' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>EVIDENCE</text>
  {"".join(rows)}
    """
    return shell("Tool matrix for schema and evidence posture.", "High-risk tools stay visible even when the server surface looks healthy.", body)


def audit_svg() -> str:
    body = f"""
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>AUDIT METHODOLOGY</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>How posture gets assigned.</text>
  <text x='356' y='492' fill='#93a7c5' font-size='15' font-family='Segoe UI'>The score reflects the real questions operators and security leads ask.</text>
  <rect x='356' y='526' width='520' height='104' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='554' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>AUTHENTICATION MODEL</text>
  <text x='382' y='586' fill='#f6f8fe' font-size='16' font-family='Segoe UI' font-weight='700'>Can the identity lane survive production pressure?</text>
  <text x='382' y='614' fill='#93a7c5' font-size='13' font-family='Segoe UI'>Legacy API-key trust drags the score because it weakens tenant accountability.</text>
  <rect x='356' y='646' width='520' height='104' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='674' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>NETWORK ZONING</text>
  <text x='382' y='706' fill='#f6f8fe' font-size='16' font-family='Segoe UI' font-weight='700'>Does the server live inside a defendable boundary?</text>
  <text x='382' y='734' fill='#93a7c5' font-size='13' font-family='Segoe UI'>Internet-reachable servers must earn that exposure with stronger approvals.</text>
  <rect x='900' y='526' width='648' height='256' rx='22' fill='rgba(2,6,12,0.92)' stroke='rgba(255,255,255,0.08)'/>
  <text x='928' y='556' fill='#6ec5ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>EVAL_ENGINE_STRICT.PY</text>
  <text x='928' y='598' fill='#d9e6ff' font-size='13' font-family='Courier New'>if auth == 'api-key': risk += 18</text>
  <text x='928' y='626' fill='#d9e6ff' font-size='13' font-family='Courier New'>if network == 'internet-reachable': risk += 16</text>
  <text x='928' y='654' fill='#d9e6ff' font-size='13' font-family='Courier New'>if destructive and not approval: risk += 15</text>
  <text x='928' y='682' fill='#d9e6ff' font-size='13' font-family='Courier New'>if schema &lt; 70: risk += 8</text>
  <text x='928' y='710' fill='#d9e6ff' font-size='13' font-family='Courier New'>if evidence &lt; 60: risk += 8</text>
  <text x='928' y='752' fill='#93a7c5' font-size='12' font-family='Segoe UI'>Operator-first. CISO-legible. CI-native.</text>
    """
    return shell("How posture gets assigned.", "The score reflects the real questions operators and security leads ask.", body)


def main() -> None:
    (OUT_DIR / "01-overview.svg").write_text(overview_svg(), encoding="utf-8")
    (OUT_DIR / "02-policy-queue.svg").write_text(policy_queue_svg(), encoding="utf-8")
    (OUT_DIR / "03-tool-matrix.svg").write_text(tool_matrix_svg(), encoding="utf-8")
    (OUT_DIR / "04-audit-methodology.svg").write_text(audit_svg(), encoding="utf-8")
    print("rendered screenshots")


if __name__ == "__main__":
    main()
