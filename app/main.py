from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.render import render_api_summary, render_overview, render_policy_queue, render_tool_matrix
from app.services.policy_service import build_service

app = FastAPI(
    title="MCP Policy Lab",
    version="0.1.0",
    description=(
        "Policy evaluation and review lab for MCP servers and tools, focused on "
        "destructive-action controls, schema posture, and operator-facing trust decisions."
    ),
)

SERVICE = build_service()


@app.get("/", response_class=HTMLResponse)
def overview() -> str:
    return render_overview()


@app.get("/policies", response_class=HTMLResponse)
def policies() -> str:
    return render_policy_queue()


@app.get("/tool-matrix", response_class=HTMLResponse)
def tool_matrix() -> str:
    return render_tool_matrix()


@app.get("/api-summary", response_class=HTMLResponse)
def api_summary() -> str:
    return render_api_summary()


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict:
    return SERVICE.summary()


@app.get("/api/servers")
def servers() -> list[dict]:
    return SERVICE.server_catalog()


@app.get("/api/servers/{server_id}")
def server_detail(server_id: str) -> dict:
    server = SERVICE.server_detail(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@app.get("/api/tools")
def tools() -> list[dict]:
    return SERVICE.tool_matrix()


@app.get("/api/evaluations")
def evaluations() -> list[dict]:
    return SERVICE.policy_queue()


@app.get("/api/sample")
def sample() -> dict:
    return SERVICE.sample_payload()


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "4926"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
