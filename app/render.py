from __future__ import annotations

import json
from html import escape
from statistics import mean

from app.services.policy_service import build_service


SERVICE = build_service()


def _server_lookup() -> dict[str, dict]:
    return {server["serverId"]: server for server in SERVICE.servers}


def _verdict_class(verdict: str) -> str:
    return {
        "stable": "stable",
        "review": "review",
        "contain": "contain",
    }[verdict]


def _risk_class(risk_class: str) -> str:
    return {
        "low": "risk-low",
        "medium": "risk-medium",
        "high": "risk-high",
        "critical": "risk-critical",
    }[risk_class]


def _format_metric_label(label: str) -> str:
    return label.replace("_", " ").replace("-", " ").title()


def _score_bars(server: dict) -> str:
    metrics = [
        ("Approval hygiene", max(0, min(100, server["humanApprovalRate"]))),
        ("Schema recency", max(0, 100 - min(server["schemaReviewDays"], 100))),
        ("Evidence retention", max(0, min(100, round(server["evidenceRetentionDays"] / 3.65)))),
        ("Tool gating", round(mean(100 if tool["requiresApproval"] else 35 for tool in server["tools"]), 1)),
    ]
    rows = []
    for label, value in metrics:
        tone = "good" if value >= 80 else "watch" if value >= 60 else "hot"
        rows.append(
            f"""
            <div class="meter-row">
              <div class="meter-head">
                <span>{escape(label)}</span>
                <span>{round(value)}%</span>
              </div>
              <div class="meter-track"><div class="meter-fill {tone}" style="width: {value:.1f}%"></div></div>
            </div>
            """
        )
    return "".join(rows)


def _shell(title: str, subtitle: str, current: str, body: str) -> str:
    summary = SERVICE.summary()
    nav_items = [
        ("/", "Overview", "overview"),
        ("/policies", "Policy Queue", "policies"),
        ("/tool-matrix", "Tool Matrix", "tools"),
        ("/audit", "Audit Methodology", "audit"),
    ]
    nav = "".join(
        f"""
        <a class="side-link {'active' if key == current else ''}" href="{href}">
          <span class="side-link-label">{escape(label)}</span>
        </a>
        """
        for href, label, key in nav_items
    )
    header_nav = "".join(
        f"""<a class="tab-pill {'active' if key == current else ''}" href="{href}">{escape(label)}</a>"""
        for href, label, key in nav_items
    )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #050912;
        --bg-2: #091321;
        --panel: rgba(10, 18, 33, 0.88);
        --panel-strong: rgba(7, 13, 24, 0.94);
        --panel-soft: rgba(255, 255, 255, 0.045);
        --line: rgba(120, 163, 214, 0.16);
        --line-strong: rgba(78, 148, 246, 0.22);
        --text: #f6f8fe;
        --muted: #93a7c5;
        --cyan: #6ec5ff;
        --blue: #4b8eff;
        --green: #44d39d;
        --amber: #f4c76d;
        --red: #ff7a88;
        --shadow: 0 28px 70px rgba(0, 0, 0, 0.42);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, "Segoe UI", system-ui, sans-serif;
        color: var(--text);
        background:
          radial-gradient(circle at top left, rgba(82, 150, 255, 0.15), transparent 28%),
          radial-gradient(circle at top right, rgba(68, 211, 157, 0.08), transparent 20%),
          linear-gradient(180deg, #02050b 0%, var(--bg) 45%, #03070f 100%);
      }}
      a {{ color: inherit; }}
      .shell {{
        min-height: 100vh;
        display: grid;
        grid-template-columns: 248px minmax(0, 1fr);
      }}
      .sidebar {{
        background: rgba(0, 0, 0, 0.28);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(18px);
        padding: 24px 18px;
        display: flex;
        flex-direction: column;
        gap: 18px;
      }}
      .brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 10px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      }}
      .brand-mark {{
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: grid;
        place-items: center;
        color: white;
        font-weight: 800;
        background: linear-gradient(135deg, #0b93c7, #3978ff);
        box-shadow: 0 0 18px rgba(75, 142, 255, 0.38);
      }}
      .brand-copy strong {{
        display: block;
        font-size: 14px;
        letter-spacing: 0.02em;
      }}
      .brand-copy span {{
        display: block;
        margin-top: 4px;
        font-size: 10px;
        color: var(--cyan);
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }}
      .side-link {{
        display: block;
        padding: 13px 14px;
        border: 1px solid transparent;
        border-radius: 14px;
        color: #7f92ae;
        text-decoration: none;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        transition: all 160ms ease;
      }}
      .side-link:hover {{
        color: var(--text);
        background: rgba(255, 255, 255, 0.04);
      }}
      .side-link.active {{
        color: var(--cyan);
        background: rgba(110, 197, 255, 0.08);
        border-color: rgba(110, 197, 255, 0.18);
        box-shadow: inset 0 0 0 1px rgba(110, 197, 255, 0.04);
      }}
      .side-meta {{
        margin-top: auto;
        padding: 16px 12px 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
      }}
      .side-meta dt {{
        color: #687b95;
        font-size: 10px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 4px;
      }}
      .side-meta dd {{
        margin: 0 0 14px;
        font-size: 12px;
        color: var(--text);
        font-weight: 700;
      }}
      .main {{
        min-width: 0;
      }}
      .topbar {{
        position: sticky;
        top: 0;
        z-index: 2;
        height: 72px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 0 34px;
        background: rgba(0, 0, 0, 0.34);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
      }}
      .status-chip {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 9px 14px;
        border-radius: 999px;
        border: 1px solid rgba(110, 197, 255, 0.14);
        background: rgba(110, 197, 255, 0.05);
        color: #a8d8ff;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }}
      .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--cyan);
        box-shadow: 0 0 12px rgba(110, 197, 255, 0.85);
      }}
      .topbar-right {{
        display: flex;
        align-items: center;
        gap: 20px;
      }}
      .meta-block {{
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
      }}
      .meta-block strong {{
        color: var(--text);
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }}
      .meta-block span {{
        color: #6c7e98;
        font-size: 9px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
      }}
      .action-pill {{
        display: inline-flex;
        align-items: center;
        padding: 12px 16px;
        border-radius: 999px;
        color: white;
        text-decoration: none;
        background: linear-gradient(135deg, #0f8fbf, #316aff);
        box-shadow: 0 0 20px rgba(57, 120, 255, 0.28);
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }}
      .wrap {{
        max-width: 1280px;
        margin: 0 auto;
        padding: 34px;
      }}
      .hero {{
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 28px;
        background:
          linear-gradient(180deg, rgba(10, 18, 33, 0.95), rgba(6, 11, 20, 0.94)),
          radial-gradient(circle at top right, rgba(75, 142, 255, 0.14), transparent 28%);
        box-shadow: var(--shadow);
      }}
      .hero-eyebrow {{
        margin-bottom: 18px;
        color: var(--cyan);
        font-size: 11px;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        font-weight: 800;
      }}
      h1 {{
        margin: 0;
        font-size: clamp(38px, 5vw, 72px);
        line-height: 0.92;
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: -0.04em;
      }}
      .hero-subtitle {{
        max-width: 820px;
        margin-top: 14px;
        color: var(--muted);
        font-size: 19px;
        line-height: 1.55;
      }}
      .hero-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin-top: 24px;
      }}
      .hero-kpi {{
        min-width: 170px;
        padding: 14px 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.035);
      }}
      .hero-kpi .k {{
        color: #6e82a1;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-weight: 800;
      }}
      .hero-kpi .v {{
        margin-top: 6px;
        font-size: 28px;
        font-weight: 800;
      }}
      .hero-callout {{
        margin-top: 18px;
        padding: 18px 20px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        background: rgba(2, 8, 17, 0.62);
      }}
      .hero-callout strong {{
        display: block;
        color: var(--cyan);
        font-size: 10px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }}
      .hero-callout p {{
        margin: 0;
        color: #d7e5fb;
        font-size: 17px;
        line-height: 1.5;
      }}
      .tab-row {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 20px;
      }}
      .tab-pill {{
        display: inline-flex;
        align-items: center;
        text-decoration: none;
        padding: 10px 14px;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.03);
        color: #afc0d8;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }}
      .tab-pill.active {{
        color: var(--cyan);
        border-color: rgba(110, 197, 255, 0.16);
        background: rgba(110, 197, 255, 0.08);
      }}
      .page-section {{
        margin-top: 24px;
        border: 1px solid var(--line);
        border-radius: 26px;
        background: var(--panel);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.24);
        overflow: hidden;
      }}
      .section-head {{
        padding: 20px 24px 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      }}
      .section-head strong {{
        display: block;
        color: var(--cyan);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 10px;
      }}
      .section-head h2 {{
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 24px;
        letter-spacing: -0.03em;
      }}
      .section-head p {{
        margin: 10px 0 0;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.55;
      }}
      .section-body {{
        padding: 24px;
      }}
      .stats-grid {{
        display: grid;
        gap: 18px;
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }}
      .stat-card {{
        border-radius: 20px;
        padding: 18px 18px 20px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(0, 0, 0, 0.08));
      }}
      .stat-card .label {{
        color: #71839d;
        font-size: 10px;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-weight: 800;
      }}
      .stat-card .value {{
        margin-top: 10px;
        font-size: 38px;
        font-weight: 900;
      }}
      .stat-card .sub {{
        margin-top: 10px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.45;
      }}
      .insight-grid {{
        display: grid;
        gap: 18px;
        grid-template-columns: 1.4fr 1fr;
      }}
      .panel {{
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(4, 9, 18, 0.55);
        padding: 22px;
      }}
      .panel h3 {{
        margin: 0 0 16px;
        color: var(--text);
        font-size: 18px;
        letter-spacing: -0.02em;
      }}
      .panel-grid {{
        display: grid;
        gap: 14px;
      }}
      .metric-card {{
        padding: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.028);
      }}
      .metric-card .micro {{
        color: #6f83a0;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-weight: 800;
      }}
      .metric-card .title {{
        margin-top: 8px;
        font-size: 15px;
        font-weight: 800;
        color: var(--text);
      }}
      .metric-card .desc {{
        margin-top: 8px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
      }}
      .meter-row + .meter-row {{
        margin-top: 14px;
      }}
      .meter-head {{
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 8px;
        color: #cfe0f7;
        font-size: 12px;
        font-weight: 700;
      }}
      .meter-track {{
        height: 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.05);
        overflow: hidden;
      }}
      .meter-fill {{
        height: 100%;
        border-radius: 999px;
      }}
      .meter-fill.good {{
        background: linear-gradient(90deg, #1e7fc7, #44d39d);
        box-shadow: 0 0 18px rgba(68, 211, 157, 0.22);
      }}
      .meter-fill.watch {{
        background: linear-gradient(90deg, #2f82ff, #f4c76d);
        box-shadow: 0 0 18px rgba(244, 199, 109, 0.22);
      }}
      .meter-fill.hot {{
        background: linear-gradient(90deg, #d14d6c, #ff7a88);
        box-shadow: 0 0 18px rgba(255, 122, 136, 0.2);
      }}
      .server-grid {{
        display: grid;
        gap: 16px;
      }}
      .server-card {{
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(4, 9, 18, 0.6);
        overflow: hidden;
      }}
      .server-card-top {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto auto;
        gap: 18px;
        align-items: center;
        padding: 20px 22px;
      }}
      .server-card h3 {{
        margin: 0;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.03em;
      }}
      .server-card .meta {{
        margin-top: 8px;
        color: var(--muted);
        font-size: 13px;
      }}
      .tag {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 8px 12px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        border: 1px solid transparent;
      }}
      .stable {{
        color: var(--green);
        background: rgba(68, 211, 157, 0.12);
        border-color: rgba(68, 211, 157, 0.16);
      }}
      .review {{
        color: var(--amber);
        background: rgba(244, 199, 109, 0.12);
        border-color: rgba(244, 199, 109, 0.16);
      }}
      .contain {{
        color: var(--red);
        background: rgba(255, 122, 136, 0.12);
        border-color: rgba(255, 122, 136, 0.16);
      }}
      .score-stack {{
        text-align: right;
      }}
      .score-stack .micro {{
        color: #6f83a0;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-weight: 800;
      }}
      .score-stack .value {{
        margin-top: 6px;
        font-size: 28px;
        font-weight: 900;
      }}
      .server-card-bottom {{
        padding: 18px 22px 22px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(255, 255, 255, 0.02);
      }}
      .server-grid.two {{
        grid-template-columns: 1fr 1fr;
      }}
      .table-shell {{
        overflow: hidden;
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(4, 9, 18, 0.58);
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
      }}
      th, td {{
        padding: 16px 18px;
        text-align: left;
        vertical-align: top;
      }}
      thead th {{
        color: #7385a0;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        background: rgba(255, 255, 255, 0.035);
      }}
      tbody tr + tr td {{
        border-top: 1px solid rgba(255, 255, 255, 0.05);
      }}
      tbody tr:hover td {{
        background: rgba(110, 197, 255, 0.03);
      }}
      .subtext {{
        margin-top: 6px;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.45;
      }}
      .risk-badge {{
        display: inline-flex;
        align-items: center;
        padding: 7px 10px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.15em;
        text-transform: uppercase;
      }}
      .risk-low {{
        color: #b7c7de;
        background: rgba(183, 199, 222, 0.12);
      }}
      .risk-medium {{
        color: var(--cyan);
        background: rgba(110, 197, 255, 0.12);
      }}
      .risk-high {{
        color: var(--amber);
        background: rgba(244, 199, 109, 0.12);
      }}
      .risk-critical {{
        color: var(--red);
        background: rgba(255, 122, 136, 0.12);
      }}
      .yes {{
        color: var(--green);
        font-weight: 800;
      }}
      .no {{
        color: var(--red);
        font-weight: 800;
      }}
      .pill-stack {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }}
      .code-panel {{
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(2, 6, 12, 0.92);
        padding: 18px 20px 20px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
      }}
      .code-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }}
      .code-head span {{
        color: var(--cyan);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }}
      .lights {{
        display: flex;
        gap: 7px;
      }}
      .lights i {{
        display: block;
        width: 9px;
        height: 9px;
        border-radius: 50%;
      }}
      .lights i:nth-child(1) {{ background: rgba(255, 122, 136, 0.7); }}
      .lights i:nth-child(2) {{ background: rgba(244, 199, 109, 0.7); }}
      .lights i:nth-child(3) {{ background: rgba(68, 211, 157, 0.7); }}
      pre {{
        margin: 0;
        overflow: auto;
        white-space: pre-wrap;
        color: #d9e6ff;
        font-size: 13px;
        line-height: 1.6;
        font-family: "Cascadia Code", Consolas, monospace;
      }}
      .footer-strip {{
        margin-top: 18px;
        display: flex;
        justify-content: space-between;
        gap: 16px;
        color: #6c7d96;
        font-size: 10px;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        padding: 4px 2px 10px;
      }}
      .footer-strip strong {{
        color: #b8c8de;
      }}
      @media (max-width: 1080px) {{
        .shell {{
          grid-template-columns: 1fr;
        }}
        .sidebar {{
          display: none;
        }}
        .stats-grid,
        .insight-grid,
        .server-grid.two {{
          grid-template-columns: 1fr;
        }}
        .server-card-top {{
          grid-template-columns: 1fr;
          align-items: start;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark">PL</div>
          <div class="brand-copy">
            <strong>MCP Policy Lab</strong>
            <span>Instance: POL-ALPHA</span>
          </div>
        </div>
        <nav>{nav}</nav>
        <dl class="side-meta">
          <dt>Region</dt>
          <dd>US-WEST-2</dd>
          <dt>Postural status</dt>
          <dd>Operational</dd>
          <dt>Review pressure</dt>
          <dd>{summary["criticalServers"]} contain / {summary["watchServers"]} review</dd>
        </dl>
      </aside>
      <main class="main">
        <header class="topbar">
          <div class="status-chip"><span class="status-dot"></span>Safety feed active</div>
          <div class="topbar-right">
            <div class="meta-block">
              <span>Control zone</span>
              <strong>Policy / Governance</strong>
            </div>
            <div class="meta-block">
              <span>Lead lane</span>
              <strong>{summary["criticalServers"]} containment</strong>
            </div>
            <a class="action-pill" href="/docs">Open API docs</a>
          </div>
        </header>
        <div class="wrap">
          <section class="hero">
            <div class="hero-eyebrow">MCP Policy Lab</div>
            <h1>{escape(title)}</h1>
            <p class="hero-subtitle">{escape(subtitle)}</p>
            <div class="hero-strip">
              <div class="hero-kpi"><div class="k">Servers under review</div><div class="v">{summary["serverCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Critical containment lanes</div><div class="v">{summary["criticalServers"]}</div></div>
              <div class="hero-kpi"><div class="k">Average risk score</div><div class="v">{summary["averageRiskScore"]}</div></div>
              <div class="hero-kpi"><div class="k">Tool inventory</div><div class="v">{summary["toolCount"]}</div></div>
            </div>
            <div class="hero-callout">
              <strong>Lead recommendation</strong>
              <p>{escape(summary["leadRecommendation"])}</p>
            </div>
            <div class="tab-row">{header_nav}</div>
          </section>
          {body}
          <div class="footer-strip">
            <span><strong>Protocol:</strong> MCP-P-2024</span>
            <span><strong>Retention:</strong> Audit-ready evidence lanes</span>
            <span><strong>Surface:</strong> Operator-first / CI-native / CISO-legible</span>
          </div>
        </div>
      </main>
    </div>
  </body>
</html>"""


def render_overview() -> str:
    summary = SERVICE.summary()
    catalog = SERVICE.server_catalog()
    raw_servers = _server_lookup()
    auth_avg = round(
        mean(
            {
                "api-key": 32,
                "oidc": 86,
                "workload-jwt": 93,
            }[server["authModel"]]
            for server in SERVICE.servers
        ),
        1,
    )
    network_avg = round(
        mean(
            {
                "internet-reachable": 26,
                "shared-control": 76,
                "internal": 92,
            }[server["networkZone"]]
            for server in SERVICE.servers
        ),
        1,
    )
    approval_avg = round(mean(server["humanApprovalRate"] for server in SERVICE.servers), 1)
    aggregate_metrics = {
        "humanApprovalRate": approval_avg,
        "schemaReviewDays": max(0, round(100 - summary["averageSchemaCoverage"])),
        "evidenceRetentionDays": round(summary["averageEvidenceCoverage"] * 3.65),
        "tools": [
            {"requiresApproval": True},
            {"requiresApproval": True},
        ],
    }
    metrics_panel = f"""
      <div class="panel">
        <h3>Average trust metrics</h3>
        {_score_bars(aggregate_metrics)}
        <div class="panel-grid" style="margin-top: 18px;">
          <div class="metric-card">
            <div class="micro">Auth model average</div>
            <div class="title">{auth_avg}% confidence lane</div>
            <div class="desc">JWT and OIDC lanes are holding, but legacy API-key trust still drags the surface down.</div>
          </div>
          <div class="metric-card">
            <div class="micro">Network zoning</div>
            <div class="title">{network_avg}% isolation quality</div>
            <div class="desc">Internet-reachable servers remain the fastest path to containment pressure.</div>
          </div>
        </div>
      </div>
    """

    board_rows = []
    for item in catalog:
        raw = raw_servers[item["serverId"]]
        board_rows.append(
            f"""
            <div class="server-card">
              <div class="server-card-top">
                <div>
                  <h3>{escape(item["name"])}</h3>
                  <div class="meta">{escape(item["owner"])} · {escape(item["environment"])} · {escape(item["authModel"])} · {escape(item["networkZone"])}</div>
                </div>
                <span class="tag {_verdict_class(item["verdict"])}">{escape(item["verdict"])}</span>
                <div class="score-stack">
                  <div class="micro">Risk score</div>
                  <div class="value">{item["riskScore"]}</div>
                </div>
              </div>
              <div class="server-card-bottom">
                <div class="server-grid two">
                  <div>
                    {_score_bars(raw)}
                  </div>
                  <div class="panel-grid">
                    <div class="metric-card">
                      <div class="micro">Top concern</div>
                      <div class="title">{escape(item["nextAction"].split(".")[0])}</div>
                      <div class="desc">{escape(item["nextAction"])}</div>
                    </div>
                    <div class="metric-card">
                      <div class="micro">Coverage posture</div>
                      <div class="title">Schema {item["schemaCoverage"]}% · Evidence {item["evidenceCoverage"]}%</div>
                      <div class="desc">{raw["toolCount"]} tools are currently attached to this trust lane.</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """
        )

    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Command surface</strong>
          <h2>Control-plane summary for MCP trust posture.</h2>
          <p>Server count, critical lanes, trust metrics, and operator recommendations at a glance.</p>
        </div>
        <div class="section-body">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="label">Servers</div>
              <div class="value">{summary["serverCount"]}</div>
              <div class="sub">Policy-evaluated MCP servers across internal, shared-control, and internet-facing lanes.</div>
            </div>
            <div class="stat-card">
              <div class="label">Review required</div>
              <div class="value">{summary["watchServers"]}</div>
              <div class="sub">Servers that are still eligible for operator review instead of immediate containment.</div>
            </div>
            <div class="stat-card">
              <div class="label">Containment pressure</div>
              <div class="value">{summary["criticalServers"]}</div>
              <div class="sub">Servers that should not expand trust until destructive controls and evidence gaps are fixed.</div>
            </div>
            <div class="stat-card">
              <div class="label">Average evidence</div>
              <div class="value">{summary["averageEvidenceCoverage"]}%</div>
              <div class="sub">Evidence retention quality across the current tool surface.</div>
            </div>
          </div>
          <div class="insight-grid" style="margin-top: 20px;">
            {metrics_panel}
            <div class="panel">
              <h3>Operator notes</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Containment lane</div>
                  <div class="title">Growth Ops MCP is still the main exception path.</div>
                  <div class="desc">Legacy API-key auth, weak approvals, and low evidence coverage are stacking into a full contain verdict.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Healthiest lane</div>
                  <div class="title">Core Bridge remains reviewable and audit-friendly.</div>
                  <div class="desc">Its destructive tools are still high risk, but they are held behind human approval and strong evidence retention.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">What to harden next</div>
                  <div class="title">Schema refresh cadence</div>
                  <div class="desc">Review lanes should tighten stale schema reviews before they become silent operator trust debt.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="page-section">
        <div class="section-head">
          <strong>Server posture board</strong>
          <h2>Every trust lane stays visible.</h2>
          <p>The point is not just scoring servers. It is showing where a CISO or platform operator would intervene first.</p>
        </div>
        <div class="section-body">
          <div class="server-grid">
            {"".join(board_rows)}
          </div>
        </div>
      </section>
    """
    return _shell(
        "Governance overview",
        "Evaluating MCP server trust posture, destructive-action gating, and operator evidence quality.",
        "overview",
        body,
    )


def render_policy_queue() -> str:
    queue = SERVICE.policy_queue()
    raw_servers = _server_lookup()
    cards = []
    for item in queue:
        raw = raw_servers[item["serverId"]]
        trigger_tools = [
            f'<span class="risk-badge {_risk_class(tool["riskClass"])}">{escape(tool["name"])}</span>'
            for tool in raw["tools"]
            if tool["destructive"] or not tool["requiresApproval"]
        ]
        cards.append(
            f"""
            <div class="server-card">
              <div class="server-card-top">
                <div>
                  <h3>{escape(item["name"])}</h3>
                  <div class="meta">{escape(item["owner"])} · {escape(raw["environment"])} · {escape(raw["authModel"])} · {raw["toolCount"]} tools</div>
                </div>
                <span class="tag {_verdict_class(item["verdict"])}">{escape(item["verdict"])}</span>
                <div class="score-stack">
                  <div class="micro">Risk score</div>
                  <div class="value">{item["riskScore"]}</div>
                </div>
              </div>
              <div class="server-card-bottom">
                <div class="server-grid two">
                  <div>
                    <div class="metric-card">
                      <div class="micro">Policy gap</div>
                      <div class="title">{escape(item["policyGap"])}</div>
                      <div class="desc">{escape(item["nextAction"])}</div>
                    </div>
                    <div class="metric-card" style="margin-top: 14px;">
                      <div class="micro">Review trigger set</div>
                      <div class="pill-stack">
                        {"".join(trigger_tools) or '<span class="risk-badge risk-low">No urgent trigger</span>'}
                      </div>
                    </div>
                  </div>
                  <div>
                    {_score_bars(raw)}
                  </div>
                </div>
              </div>
            </div>
            """
        )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Review queue</strong>
          <h2>Review queue for destructive-action exposure.</h2>
          <p>The servers most likely to need containment or human review stay at the top, with the gap and next action spelled out instead of hidden behind a score.</p>
        </div>
        <div class="section-body">
          <div class="server-grid">
            {"".join(cards)}
          </div>
        </div>
      </section>
    """
    return _shell(
        "Policy queue",
        "Servers triaged by risk posture, destructive-action exposure, and evidence gaps.",
        "policies",
        body,
    )


def render_tool_matrix() -> str:
    matrix = SERVICE.tool_matrix()
    risk_counts = {
        "critical": sum(1 for item in matrix if item["riskClass"] == "critical"),
        "high": sum(1 for item in matrix if item["riskClass"] == "high"),
        "medium": sum(1 for item in matrix if item["riskClass"] == "medium"),
        "low": sum(1 for item in matrix if item["riskClass"] == "low"),
    }
    rows = "".join(
        f"""
        <tr>
          <td>
            <strong>{escape(item["toolName"])}</strong>
            <div class="subtext">{escape(item["serverName"])}</div>
          </td>
          <td><span class="risk-badge {_risk_class(item["riskClass"])}">{escape(item["riskClass"])}</span></td>
          <td class="{'yes' if item['destructive'] else 'no'}">{'Yes' if item['destructive'] else 'No'}</td>
          <td class="{'yes' if item['requiresApproval'] else 'no'}">{'Yes' if item['requiresApproval'] else 'No'}</td>
          <td>{item['schemaCoverage']}%</td>
          <td>{item['evidenceCoverage']}%</td>
        </tr>
        """
        for item in matrix
    )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Tool inventory</strong>
          <h2>Tool matrix for schema and evidence posture.</h2>
          <p>High-risk tools stay visible even when the server surface looks healthy. This is the layer operators actually need when deciding what to gate, review, or contain.</p>
        </div>
        <div class="section-body">
          <div class="stats-grid" style="grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 20px;">
            <div class="stat-card"><div class="label">Critical tools</div><div class="value">{risk_counts["critical"]}</div><div class="sub">Destructive lanes that should always be reviewable.</div></div>
            <div class="stat-card"><div class="label">High-risk tools</div><div class="value">{risk_counts["high"]}</div><div class="sub">State-changing actions that still need strong approval hygiene.</div></div>
            <div class="stat-card"><div class="label">Medium-risk tools</div><div class="value">{risk_counts["medium"]}</div><div class="sub">Often safe enough for operators, but still meaningful to trace.</div></div>
            <div class="stat-card"><div class="label">Low-risk tools</div><div class="value">{risk_counts["low"]}</div><div class="sub">Mostly read-only or low-impact inventory surfaces.</div></div>
          </div>
          <div class="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Tool identity</th>
                  <th>Risk status</th>
                  <th>Destructive</th>
                  <th>Approval</th>
                  <th>Schema</th>
                  <th>Evidence</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Tool inventory",
        "Inventory of all active MCP tools and their evaluated risk signature.",
        "tools",
        body,
    )


def render_audit_summary() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Audit methodology</strong>
          <h2>How posture gets assigned.</h2>
          <p>This is not a toy scorecard. It reflects the real questions operators and security leads ask when an MCP surface moves from demo to production.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="panel">
              <h3>Posture allocation factors</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Authentication model</div>
                  <div class="title">Can the identity lane survive production pressure?</div>
                  <div class="desc">Legacy API-key trust drags the score hard because it hides tenant isolation and human accountability.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Network zoning</div>
                  <div class="title">Does the server live inside a defendable boundary?</div>
                  <div class="desc">Internet-reachable MCP servers are not automatically bad, but they must earn that exposure with stronger approvals and evidence.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Schema + evidence hygiene</div>
                  <div class="title">Can a human understand and review what the tool is about to do?</div>
                  <div class="desc">Weak schema coverage and thin evidence retention are how safe-looking demos become post-incident blind spots.</div>
                </div>
              </div>
            </div>
            <div class="panel">
              <div class="code-panel">
                <div class="code-head">
                  <span>eval_engine_strict.py</span>
                  <div class="lights"><i></i><i></i><i></i></div>
                </div>
                <pre><code>{escape(payload)}</code></pre>
              </div>
            </div>
          </div>
          <div class="server-grid two" style="margin-top: 18px;">
            <div class="metric-card">
              <div class="micro">Design philosophy</div>
              <div class="title">Operator-first, CISO-legible, CI-native.</div>
              <div class="desc">The output should be useful in a queue, a pull request gate, or an incident review. That is why verdicts, next actions, and evidence posture are all first-class.</div>
            </div>
            <div class="metric-card">
              <div class="micro">Current compliance note</div>
              <div class="title">Contain lanes should stay hardware-gated.</div>
              <div class="desc">Any destructive lane in contain should require an explicit human approval boundary before the surface expands again.</div>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Audit methodology",
        "How mcp-policy-lab scores tool risk, server posture, and operator review pressure.",
        "audit",
        body,
    )


def render_api_summary() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>API summary</strong>
          <h2>Structured outputs for CI and governance workflows.</h2>
          <p>The same posture model can feed approval workflows, incident reviews, or broader MCP governance platforms without losing human-readable context.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="panel">
              <h3>Why the payload matters</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Review queues</div>
                  <div class="title">Route the right server to the right human.</div>
                  <div class="desc">Verdict, policy gap, and next action are all present because operators need more than a number.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">CI gates</div>
                  <div class="title">Block trust expansion when posture drops.</div>
                  <div class="desc">A control plane can reject new tools or environments if contain lanes are still unresolved.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Audit trails</div>
                  <div class="title">Keep evidence posture tied to the decision.</div>
                  <div class="desc">Schema and evidence coverage are part of the same surface so governance does not drift away from operations.</div>
                </div>
              </div>
            </div>
            <div class="panel">
              <div class="code-panel">
                <div class="code-head">
                  <span>/api/sample</span>
                  <div class="lights"><i></i><i></i><i></i></div>
                </div>
                <pre><code>{escape(payload)}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "API summary",
        "The policy surface is designed for operator workflows as much as dashboards.",
        "audit",
        body,
    )
