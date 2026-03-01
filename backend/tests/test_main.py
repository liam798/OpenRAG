import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class MainAppTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_live_health_and_request_id(self):
        response = self.client.get("/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Process-Time-Ms", response.headers)

    @patch("app.main.check_db_health", return_value=(True, "ok"))
    def test_ready_health_ok(self, _mock_health):
        response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("app.main.check_db_health", return_value=(False, "db unavailable"))
    def test_ready_health_degraded(self, _mock_health):
        response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["status"], "degraded")
        self.assertIn("database", body)


if __name__ == "__main__":
    unittest.main()
