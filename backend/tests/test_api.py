import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


class TestDevFlowAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "operational")
        self.assertEqual(data["version"], "1.0.0")

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_list_projects(self):
        response = self.client.get("/projects")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["projects"]), 1)

    def test_get_project(self):
        response = self.client.get("/projects/demo-project-001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "demo-project-001")

    def test_analyze_project(self):
        response = self.client.post("/projects/demo-project-001/analyze")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("health_score", data)
        self.assertIn("issues", data)
        self.assertGreaterEqual(len(data["issues"]), 1)

    def test_generate_fix(self):
        payload = {
            "issue_id": "ISSUE-001",
            "project_id": "demo-project-001"
        }
        response = self.client.post("/issues/fix", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["issue_id"], "ISSUE-001")
        self.assertIn("root_cause", data)
        self.assertGreaterEqual(len(data["files_to_change"]), 1)

    def test_generate_tests(self):
        payload = {
            "issue_id": "ISSUE-001",
            "project_id": "demo-project-001"
        }
        response = self.client.post("/issues/tests", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["issue_id"], "ISSUE-001")
        self.assertIn("test_cases", data)
        self.assertGreaterEqual(len(data["test_cases"]), 1)

    def test_verify_project(self):
        response = self.client.post("/projects/demo-project-001/verify")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["passed"])
        self.assertGreaterEqual(data["total_files"], 1)

    def test_release_report(self):
        response = self.client.post("/projects/demo-project-001/report")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project_id"], "demo-project-001")
        self.assertIn("release_ready", data)
        self.assertIn("health_score", data)


if __name__ == "__main__":
    unittest.main()
