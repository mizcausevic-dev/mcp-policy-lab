# Architecture

## Goal

`mcp-policy-lab` is a Python and FastAPI service for reviewing **MCP server trust posture** before the server becomes a normal part of an operator workflow. It focuses on the policy questions that usually get deferred until too late:

- Is a tool destructive?
- Does it require human approval?
- Is the schema documented enough for review?
- Will the session leave enough evidence behind to survive an incident review?
- Is the server being exposed through a trust model that matches the risk of the tools it carries?

## Service shape

The repo is intentionally small and local-first:

- `app/main.py` exposes HTML proof routes and JSON API routes.
- `app/services/policy_service.py` loads sample MCP server and tool records, evaluates risk, and produces operator-friendly queue outputs.
- `app/render.py` turns the same service state into a control-room style HTML surface.
- `scripts/run_demo.py` and `scripts/smoke_check.py` provide one-shot validation paths.
- `scripts/render_readme_assets.py` renders SVG proof assets for the README.

## Evaluation model

Each server posture is scored from:

- auth model
- network zone
- session logging
- schema review recency
- human approval rate
- evidence retention
- tool-level risk class
- destructive-action exposure
- schema coverage
- evidence coverage

The score resolves into one of three lanes:

- `stable`
- `review`
- `contain`

The output is meant to be used by platform, security, and AI governance teams that need a short list of what to inspect next.

## Why it matters

Many MCP demos stop at tool connectivity. Real operators will care more about:

- what should be gated
- what should be logged
- what should be reviewable
- what should be held back until better evidence exists

That is the layer this project is modeling.
