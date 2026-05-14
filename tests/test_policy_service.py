from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.policy_service import build_service


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

    def test_server_lookup_api(self) -> None:
        client = TestClient(app)
        response = client.get("/api/servers/srv-growth-ops")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Growth Ops MCP")


if __name__ == "__main__":
    unittest.main()
