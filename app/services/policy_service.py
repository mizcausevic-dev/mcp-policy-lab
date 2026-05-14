from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_policy_data.json"


@dataclass
class PolicyService:
    servers: list[dict]

    def summary(self) -> dict:
        evaluations = [self._evaluate_server(server) for server in self.servers]
        average_risk = round(mean(item["riskScore"] for item in evaluations), 1)
        average_schema = round(mean(item["schemaCoverage"] for item in evaluations), 1)
        average_evidence = round(mean(item["evidenceCoverage"] for item in evaluations), 1)
        critical_servers = sum(1 for item in evaluations if item["verdict"] == "contain")
        watch_servers = sum(1 for item in evaluations if item["verdict"] == "review")

        return {
            "serverCount": len(self.servers),
            "toolCount": sum(server["toolCount"] for server in self.servers),
            "criticalServers": critical_servers,
            "watchServers": watch_servers,
            "averageRiskScore": average_risk,
            "averageSchemaCoverage": average_schema,
            "averageEvidenceCoverage": average_evidence,
            "leadRecommendation": self._lead_recommendation(evaluations),
        }

    def server_catalog(self) -> list[dict]:
        evaluations = {item["serverId"]: item for item in self._evaluations()}
        rows: list[dict] = []
        for server in self.servers:
            evaluation = evaluations[server["serverId"]]
            rows.append(
                {
                    "serverId": server["serverId"],
                    "name": server["name"],
                    "owner": server["owner"],
                    "environment": server["environment"],
                    "authModel": server["authModel"],
                    "networkZone": server["networkZone"],
                    "toolCount": server["toolCount"],
                    "riskScore": evaluation["riskScore"],
                    "verdict": evaluation["verdict"],
                    "schemaCoverage": evaluation["schemaCoverage"],
                    "evidenceCoverage": evaluation["evidenceCoverage"],
                    "nextAction": evaluation["nextAction"],
                }
            )
        return sorted(rows, key=lambda row: row["riskScore"], reverse=True)

    def server_detail(self, server_id: str) -> dict | None:
        server = next((item for item in self.servers if item["serverId"] == server_id), None)
        if server is None:
            return None
        evaluation = self._evaluate_server(server)
        return {
            **server,
            "evaluation": evaluation,
            "toolMatrix": self._tool_matrix_for_server(server),
        }

    def tool_matrix(self) -> list[dict]:
        rows: list[dict] = []
        for server in self.servers:
            for tool in server["tools"]:
                rows.append(
                    {
                        "serverId": server["serverId"],
                        "serverName": server["name"],
                        "toolId": tool["toolId"],
                        "toolName": tool["name"],
                        "riskClass": tool["riskClass"],
                        "destructive": tool["destructive"],
                        "requiresApproval": tool["requiresApproval"],
                        "schemaCoverage": tool["schemaCoverage"],
                        "evidenceCoverage": tool["evidenceCoverage"],
                    }
                )
        risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return sorted(rows, key=lambda row: (risk_order[row["riskClass"]], row["schemaCoverage"]), reverse=True)

    def policy_queue(self) -> list[dict]:
        queue: list[dict] = []
        for server in self.servers:
            evaluation = self._evaluate_server(server)
            if evaluation["verdict"] == "stable":
                continue
            queue.append(
                {
                    "serverId": server["serverId"],
                    "name": server["name"],
                    "owner": server["owner"],
                    "riskScore": evaluation["riskScore"],
                    "verdict": evaluation["verdict"],
                    "policyGap": evaluation["topConcern"],
                    "nextAction": evaluation["nextAction"],
                }
            )
        return sorted(queue, key=lambda item: item["riskScore"], reverse=True)

    def sample_payload(self) -> dict:
        catalog = self.server_catalog()
        return {
            "dashboard": self.summary(),
            "highestRiskServer": catalog[0],
            "queue": self.policy_queue(),
        }

    def _evaluations(self) -> list[dict]:
        return [self._evaluate_server(server) for server in self.servers]

    def _evaluate_server(self, server: dict) -> dict:
        risk_score = 18
        if server["authModel"] == "api-key":
            risk_score += 18
        if server["networkZone"] == "internet-reachable":
            risk_score += 16
        if not server["sessionLogging"]:
            risk_score += 17
        if server["schemaReviewDays"] > 45:
            risk_score += 12
        if server["humanApprovalRate"] < 60:
            risk_score += 10
        if server["evidenceRetentionDays"] < 90:
            risk_score += 8

        for tool in server["tools"]:
            if tool["riskClass"] == "critical":
                risk_score += 12
            elif tool["riskClass"] == "high":
                risk_score += 7
            elif tool["riskClass"] == "medium":
                risk_score += 3
            if tool["destructive"] and not tool["requiresApproval"]:
                risk_score += 15
            if tool["schemaCoverage"] < 70:
                risk_score += 8
            if tool["evidenceCoverage"] < 60:
                risk_score += 8

        risk_score = min(100, risk_score)
        schema_coverage = round(mean(tool["schemaCoverage"] for tool in server["tools"]), 1)
        evidence_coverage = round(mean(tool["evidenceCoverage"] for tool in server["tools"]), 1)

        if risk_score >= 80:
            verdict = "contain"
            next_action = "Freeze destructive tools behind human approval before broader rollout."
        elif risk_score >= 55:
            verdict = "review"
            next_action = "Route the server into policy review and refresh schema/evidence coverage."
        else:
            verdict = "stable"
            next_action = "Keep the current controls and re-run the policy check after the next schema change."

        top_concern = self._top_concern(server, schema_coverage, evidence_coverage)
        return {
            "serverId": server["serverId"],
            "riskScore": risk_score,
            "schemaCoverage": schema_coverage,
            "evidenceCoverage": evidence_coverage,
            "verdict": verdict,
            "topConcern": top_concern,
            "nextAction": next_action,
        }

    def _top_concern(self, server: dict, schema_coverage: float, evidence_coverage: float) -> str:
        if server["authModel"] == "api-key":
            return "Legacy API-key auth is still carrying high-trust actions."
        if not server["sessionLogging"]:
            return "Session logging is missing for operator-critical tool usage."
        if schema_coverage < 75:
            return "Tool schemas are under-documented for safe review and approval."
        if evidence_coverage < 70:
            return "Evidence retention is too thin for post-incident review."
        if server["humanApprovalRate"] < 60:
            return "Destructive actions are bypassing human approval too often."
        return "Review pressure is rising, but the server remains within the stable policy lane."

    def _lead_recommendation(self, evaluations: list[dict]) -> str:
        critical = [item for item in evaluations if item["verdict"] == "contain"]
        if critical:
            return "Hold internet-reachable destructive tools behind approval until the containment lane clears."
        review = [item for item in evaluations if item["verdict"] == "review"]
        if review:
            return "Prioritize schema and evidence hardening before expanding server count."
        return "Current MCP posture is stable enough to add new internal tools cautiously."

    def _tool_matrix_for_server(self, server: dict) -> list[dict]:
        rows = []
        for tool in server["tools"]:
            rows.append(
                {
                    "toolId": tool["toolId"],
                    "name": tool["name"],
                    "riskClass": tool["riskClass"],
                    "destructive": tool["destructive"],
                    "requiresApproval": tool["requiresApproval"],
                    "schemaCoverage": tool["schemaCoverage"],
                    "evidenceCoverage": tool["evidenceCoverage"],
                }
            )
        return rows


def build_service() -> PolicyService:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return PolicyService(servers=payload["servers"])
