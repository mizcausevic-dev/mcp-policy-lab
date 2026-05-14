from __future__ import annotations

import json
from html import escape

from app.services.policy_service import build_service


SERVICE = build_service()


def _shell(title: str, eyebrow: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #07101b;
        --panel: #0d1a2b;
        --panel-2: #10223a;
        --line: #1d3758;
        --text: #eef4ff;
        --muted: #9ab0cf;
        --blue: #72b8ff;
        --amber: #f6be65;
        --red: #ff7f7f;
        --green: #73d2a8;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Segoe UI", Inter, sans-serif;
        background:
          radial-gradient(circle at top left, rgba(114, 184, 255, 0.12), transparent 28%),
          linear-gradient(180deg, #08111d 0%, var(--bg) 100%);
        color: var(--text);
      }}
      .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 56px; }}
      .hero {{
        border: 1px solid var(--line);
        border-radius: 24px;
        background: linear-gradient(180deg, rgba(13, 26, 43, 0.96), rgba(8, 17, 29, 0.98));
        padding: 28px;
        box-shadow: 0 24px 70px rgba(0, 0, 0, 0.32);
      }}
      .eyebrow {{
        text-transform: uppercase;
        letter-spacing: 0.22em;
        font-size: 12px;
        color: var(--blue);
        margin-bottom: 12px;
      }}
      h1 {{
        margin: 0 0 10px;
        font-size: clamp(36px, 5vw, 64px);
        line-height: 0.95;
      }}
      p.lead {{
        max-width: 760px;
        color: var(--muted);
        font-size: 18px;
        line-height: 1.55;
      }}
      .nav {{
        display: flex;
        gap: 10px;
        margin-top: 22px;
        flex-wrap: wrap;
      }}
      .nav a {{
        color: var(--text);
        text-decoration: none;
        padding: 10px 14px;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(16, 34, 58, 0.72);
        font-size: 14px;
      }}
      .grid {{
        display: grid;
        gap: 18px;
        margin-top: 22px;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      }}
      .card {{
        background: rgba(13, 26, 43, 0.92);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 18px;
      }}
      .label {{
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .value {{
        font-size: 34px;
        font-weight: 700;
      }}
      .sub {{
        color: var(--muted);
        font-size: 14px;
        margin-top: 8px;
        line-height: 1.45;
      }}
      .section {{
        margin-top: 22px;
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 22px;
        background: rgba(13, 26, 43, 0.9);
      }}
      h2 {{
        margin: 0 0 14px;
        font-size: 24px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
      }}
      th, td {{
        text-align: left;
        padding: 12px 10px;
        border-bottom: 1px solid rgba(29, 55, 88, 0.8);
        vertical-align: top;
      }}
      th {{
        color: var(--muted);
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}
      .pill {{
        display: inline-flex;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .stable {{ color: var(--green); background: rgba(115, 210, 168, 0.14); }}
      .review {{ color: var(--amber); background: rgba(246, 190, 101, 0.14); }}
      .contain {{ color: var(--red); background: rgba(255, 127, 127, 0.14); }}
      pre {{
        overflow: auto;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(6, 14, 24, 0.92);
        color: #dce9ff;
        font-size: 13px;
      }}
      code {{ font-family: "Cascadia Code", Consolas, monospace; }}
      .two-col {{
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 18px;
      }}
      @media (max-width: 860px) {{
        .two-col {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <section class="hero">
        <div class="eyebrow">{escape(eyebrow)}</div>
        <h1>MCP Policy Lab</h1>
        <p class="lead">Real-time policy evaluation for MCP servers and tools, with destructive-action gating, schema posture, evidence coverage, and operator-facing review lanes.</p>
        <div class="nav">
          <a href="/">Overview</a>
          <a href="/policies">Policy Queue</a>
          <a href="/tool-matrix">Tool Matrix</a>
          <a href="/docs">Docs</a>
          <a href="/api/sample">API Sample</a>
        </div>
      </section>
      {body}
    </div>
  </body>
</html>"""


def render_overview() -> str:
    summary = SERVICE.summary()
    rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(item['name'])}</strong><div class="sub">{escape(item['owner'])}</div></td>
          <td>{escape(item['environment'])}</td>
          <td>{escape(item['authModel'])}</td>
          <td><span class="pill {escape(item['verdict'])}">{escape(item['verdict'])}</span></td>
          <td>{item['riskScore']}</td>
          <td>{item['schemaCoverage']}%</td>
          <td>{escape(item['nextAction'])}</td>
        </tr>
        """
        for item in SERVICE.server_catalog()
    )

    body = f"""
      <div class="grid">
        <div class="card"><div class="label">Servers</div><div class="value">{summary['serverCount']}</div><div class="sub">Policy-evaluated MCP servers across internal and production lanes.</div></div>
        <div class="card"><div class="label">Tools</div><div class="value">{summary['toolCount']}</div><div class="sub">Tools scored for destructive potential, schema posture, and evidence coverage.</div></div>
        <div class="card"><div class="label">Critical</div><div class="value">{summary['criticalServers']}</div><div class="sub">Servers that should be contained before expanding trust.</div></div>
        <div class="card"><div class="label">Average Risk</div><div class="value">{summary['averageRiskScore']}</div><div class="sub">Aggregate risk across auth model, network zone, tool risk, and review hygiene.</div></div>
      </div>
      <section class="section">
        <h2>Lead recommendation</h2>
        <p class="sub">{escape(summary['leadRecommendation'])}</p>
      </section>
      <section class="section">
        <h2>Server posture board</h2>
        <table>
          <thead>
            <tr>
              <th>Server</th>
              <th>Env</th>
              <th>Auth</th>
              <th>Verdict</th>
              <th>Risk</th>
              <th>Schema</th>
              <th>Next action</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </section>
    """
    return _shell("MCP Policy Lab Overview", "Policy Control Plane", body)


def render_policy_queue() -> str:
    queue = SERVICE.policy_queue()
    rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(item['name'])}</strong><div class="sub">{escape(item['owner'])}</div></td>
          <td><span class="pill {escape(item['verdict'])}">{escape(item['verdict'])}</span></td>
          <td>{item['riskScore']}</td>
          <td>{escape(item['policyGap'])}</td>
          <td>{escape(item['nextAction'])}</td>
        </tr>
        """
        for item in queue
    )
    body = f"""
      <section class="section">
        <h2>Operator queue</h2>
        <p class="sub">This queue prioritizes the servers that need human review or containment before new tools or broader agent exposure should be allowed.</p>
        <table>
          <thead>
            <tr>
              <th>Server</th>
              <th>Verdict</th>
              <th>Risk</th>
              <th>Policy gap</th>
              <th>Next action</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </section>
    """
    return _shell("MCP Policy Queue", "Review Lane", body)


def render_tool_matrix() -> str:
    rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(item['toolName'])}</strong><div class="sub">{escape(item['serverName'])}</div></td>
          <td>{escape(item['riskClass'])}</td>
          <td>{'Yes' if item['destructive'] else 'No'}</td>
          <td>{'Yes' if item['requiresApproval'] else 'No'}</td>
          <td>{item['schemaCoverage']}%</td>
          <td>{item['evidenceCoverage']}%</td>
        </tr>
        """
        for item in SERVICE.tool_matrix()
    )
    body = f"""
      <section class="section">
        <h2>Tool matrix</h2>
        <p class="sub">A quick way to inspect which tools still combine high privilege, low approval, or weak review artifacts.</p>
        <table>
          <thead>
            <tr>
              <th>Tool</th>
              <th>Risk</th>
              <th>Destructive</th>
              <th>Approval</th>
              <th>Schema</th>
              <th>Evidence</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </section>
    """
    return _shell("MCP Tool Matrix", "Tool Review", body)


def render_api_summary() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <div class="two-col">
        <section class="section">
          <h2>Sample API payload</h2>
          <pre><code>{escape(payload)}</code></pre>
        </section>
        <section class="section">
          <h2>Why this matters</h2>
          <p class="sub">The API surface is designed for policy review workflows, not just dashboards. It returns server posture, next action, and evidence-oriented details that can plug into CI checks, governance queues, or broader MCP control planes.</p>
        </section>
      </div>
    """
    return _shell("MCP Policy API Summary", "API Summary", body)
