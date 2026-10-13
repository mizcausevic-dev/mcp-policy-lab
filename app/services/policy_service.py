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
                    "dispositionBasis": evaluation["dispositionBasis"],
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
                    "dispositionBasis": evaluation["dispositionBasis"],
                    "policyGap": evaluation["topConcern"],
                    "nextAction": evaluation["nextAction"],
                }
            )
        lane_priority = {"contain": 2, "review": 1}
        return sorted(
            queue,
            key=lambda item: (lane_priority[item["verdict"]], item["riskScore"]),
            reverse=True,
        )

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

        unapproved_destructive = any(
            tool["destructive"] and not tool["requiresApproval"] for tool in server["tools"]
        )
        missing_review_evidence = (
            not server["sessionLogging"]
            or server["evidenceRetentionDays"] < 90
            or server["schemaReviewDays"] > 45
            or (server["humanApprovalRate"] < 60 and any(tool["destructive"] for tool in server["tools"]))
            or any(
                tool["schemaCoverage"] < 70 or tool["evidenceCoverage"] < 60
                for tool in server["tools"]
            )
        )

        if unapproved_destructive or risk_score >= 80:
            verdict = "contain"
        elif missing_review_evidence or risk_score >= 55:
            verdict = "review"
        else:
            verdict = "stable"

        if unapproved_destructive:
            disposition_basis = "unapproved-destructive-hard-gate"
        elif risk_score >= 55:
            disposition_basis = "weighted-score"
        elif missing_review_evidence:
            disposition_basis = "missing-review-evidence-floor"
        else:
            disposition_basis = "sample-thresholds-met"

        top_concern, next_action = self._primary_gap(server, verdict)
        return {
            "serverId": server["serverId"],
            "riskScore": risk_score,
            "schemaCoverage": schema_coverage,
            "evidenceCoverage": evidence_coverage,
            "verdict": verdict,
            "dispositionBasis": disposition_basis,
            "topConcern": top_concern,
            "nextAction": next_action,
        }

    def _primary_gap(self, server: dict, verdict: str) -> tuple[str, str]:
        if any(tool["destructive"] and not tool["requiresApproval"] for tool in server["tools"]):
            return (
                "A destructive tool lacks a required approval gate.",
                "Disable unapproved destructive tool access until human approval is enforced and verified.",
            )
        if not server["sessionLogging"]:
            return (
                "Session logging is missing from this sample server.",
                "Enable and verify session logging before expanding tool access.",
            )
        if server["evidenceRetentionDays"] < 90 or any(
            tool["evidenceCoverage"] < 60 for tool in server["tools"]
        ):
            return (
                "The sample records insufficient evidence coverage or retention.",
                "Review evidence capture and retention against the intended incident workflow before expansion.",
            )
        if server["schemaReviewDays"] > 45 or any(
            tool["schemaCoverage"] < 70 for tool in server["tools"]
        ):
            return (
                "Tool schema coverage or review recency needs attention.",
                "Review affected tool schemas and refresh the schema review record before expansion.",
            )
        if server["authModel"] == "api-key":
            return (
                "API-key authentication needs an explicit scope review.",
                "Review the API-key scope, rotation, and caller binding for this tool set.",
            )
        if server["humanApprovalRate"] < 60 and any(
            tool["destructive"] for tool in server["tools"]
        ):
            return (
                "The sample approval rate is low for a destructive tool set.",
                "Inspect approval records and verify that destructive calls cannot bypass the gate.",
            )
        if verdict != "stable":
            return (
                "The weighted sample score calls for operator review.",
                "Review the tool risks and their deployed controls before expanding access.",
            )
        return (
            "No sample threshold was crossed.",
            "Recheck after a tool or schema change; this sample score does not authorize access.",
        )

    def _lead_recommendation(self, evaluations: list[dict]) -> str:
        for verdict in ("contain", "review"):
            lane = [item for item in evaluations if item["verdict"] == verdict]
            if lane:
                return max(lane, key=lambda item: item["riskScore"])["nextAction"]
        return "Recheck after a tool or schema change; sample scores do not authorize access."

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
