from __future__ import annotations

import unittest
from copy import deepcopy

from fastapi.testclient import TestClient

from app.main import app
from app.render import render_overview, render_policy_queue
from app.services.policy_service import PolicyService, build_service


class MCPPolicyLabTests(unittest.TestCase):
    def test_summary_shape(self) -> None:
        summary = build_service().summary()
        self.assertGreaterEqual(summary["serverCount"], 4)
        self.assertGreaterEqual(summary["toolCount"], 10)
        self.assertIn("leadRecommendation", summary)

    def test_policy_queue_has_high_risk_first(self) -> None:
        queue = build_service().policy_queue()
        self.assertGreaterEqual(queue[0]["riskScore"], queue[-1]["riskScore"])
        self.assertIn(queue[0]["verdict"], {"review", "contain"})

    def test_unapproved_destructive_tool_cannot_be_stable(self) -> None:
        server = deepcopy(build_service().servers[0])
        server["tools"] = [server["tools"][0]]
        server["tools"][0].update(destructive=True, requiresApproval=False)
        server["toolCount"] = 1
        service = PolicyService([server])
        evaluation = service.server_detail(server["serverId"])["evaluation"]
        self.assertEqual(evaluation["verdict"], "contain")
        self.assertEqual(evaluation["dispositionBasis"], "unapproved-destructive-hard-gate")
        self.assertIn("approval", evaluation["nextAction"].lower())
        self.assertIn("destructive", service.summary()["leadRecommendation"].lower())

    def test_queue_prioritizes_hard_containment_over_higher_review_score(self) -> None:
        base = build_service().servers[0]
        hard_gate = deepcopy(base)
        hard_gate["serverId"] = "hard-gate"
        hard_gate["tools"] = [hard_gate["tools"][0]]
        hard_gate["tools"][0].update(destructive=True, requiresApproval=False)
        hard_gate["toolCount"] = 1

        scored_review = deepcopy(base)
        scored_review["serverId"] = "scored-review"
        scored_review.update(authModel="api-key", networkZone="internet-reachable")
        service = PolicyService([scored_review, hard_gate])
        queue = service.policy_queue()
        self.assertGreater(queue[1]["riskScore"], queue[0]["riskScore"])
        self.assertEqual(queue[0]["serverId"], "hard-gate")
        self.assertEqual(queue[0]["dispositionBasis"], "unapproved-destructive-hard-gate")
        self.assertEqual(queue[1]["verdict"], "review")

    def test_missing_evidence_forces_review(self) -> None:
        server = deepcopy(build_service().servers[0])
        server["tools"] = [server["tools"][0]]
        server["toolCount"] = 1
        server["sessionLogging"] = False
        service = PolicyService([server])
        evaluation = service.server_detail(server["serverId"])["evaluation"]
        self.assertEqual(evaluation["verdict"], "review")
        self.assertIn("logging", evaluation["nextAction"].lower())

    def test_containment_without_destructive_tools_names_real_gap(self) -> None:
        server = deepcopy(build_service().servers[0])
        server["tools"] = [server["tools"][0]]
        server["toolCount"] = 1
        server.update(
            authModel="api-key",
            networkZone="internet-reachable",
            sessionLogging=False,
            schemaReviewDays=90,
            humanApprovalRate=40,
            evidenceRetentionDays=30,
        )
        server["tools"][0].update(schemaCoverage=50, evidenceCoverage=40)
        service = PolicyService([server])
        evaluation = service.server_detail(server["serverId"])["evaluation"]
        self.assertEqual(evaluation["verdict"], "contain")
        self.assertNotIn("destructive", evaluation["nextAction"].lower())
        self.assertNotIn("destructive", service.summary()["leadRecommendation"].lower())

    def test_overview_metrics_use_fixture_counts_not_placeholder_scores(self) -> None:
        html = render_overview()
        self.assertIn("Destructive tools marked for approval", html)
        self.assertIn("Synthetic MCP servers scored across modeled", html)
        self.assertIn("5 of 7", html)
        self.assertIn("1 of 4 use API keys", html)
        self.assertIn("1 of 4 internet-reachable", html)
        self.assertNotIn("100% confidence lane", html)
        self.assertNotIn("100% isolation quality", html)
        self.assertIn("Review queue for control and evidence gaps", render_policy_queue())

    def test_server_lookup_api(self) -> None:
        client = TestClient(app)
        response = client.get("/api/servers/srv-growth-ops")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Growth Ops MCP")

    def test_ui_discloses_synthetic_source(self) -> None:
        response = TestClient(app).get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample data · no live feed", response.text)
        self.assertIn("Bundled sample inventory", response.text)
        self.assertIn("no permission enforcement", response.text)
        self.assertNotIn("MCP-P-2024", response.text)
        self.assertNotIn("Audit-ready evidence lanes", response.text)

    def test_api_docs_disclose_sample_boundary(self) -> None:
        response = TestClient(app).get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic sample-data", response.json()["info"]["description"])


if __name__ == "__main__":
    unittest.main()
