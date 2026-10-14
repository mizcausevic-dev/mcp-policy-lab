# Local service and rollback drill, 2026-10-01

**Result: mechanical local rollback worked; release rollback remains blocked.** This was a loopback-only drill using synthetic data. It did not touch GitHub Pages, a hosted service, a real MCP server, or production traffic.

## Reproducible setup

- Candidate: review branch commit `148c15fe9fb6ef04e64005fa08eabf1a693db172` before the permission-gate edits in this PR. Its FastAPI web service is unchanged by those edits.
- Baseline: `origin/main` commit `512fd26514ef39eab6b9711c75cc2af34775d7ba`, exported with `git archive` to a separate local directory.
- Both were run with the same local Python environment using `python -m uvicorn app.main:app --host 127.0.0.1 --port 4938` from their respective directories. Each process was stopped before the other started.
- The baseline archive and expansion were kept in `C:\Users\chaus\Documents\Codex\repos\.review-drills\mcp-policy-lab-2026-10-01\` for inspection; they are not deployment artifacts.

## Observed requests

| Stage | `GET /` | `GET /api/dashboard/summary` | `GET /api/tools` | Synthetic-data disclosure |
| --- | --- | --- | --- | --- |
| Candidate | HTTP 200 | HTTP 200; 4 servers | HTTP 200; 11 tools, 11 matrix rows | Visible in HTML |
| Baseline after stop/switch | HTTP 200 | HTTP 200; 4 servers | HTTP 200; 11 tools, 11 matrix rows | **Absent** from HTML |

After stopping each process, the same loopback request failed, consistent with the local server being stopped. The successful baseline responses demonstrate that a previous commit can be restarted locally. They do not prove a production traffic switch, state or data recovery, release artifact integrity, or permission rollback. The baseline also removes the candidate's synthetic-data disclosure, so it is **not an acceptable content-equivalent release rollback target**. Before any deployment, designate and test a rollback artifact that preserves this disclosure and the permission boundary at the actual host.
