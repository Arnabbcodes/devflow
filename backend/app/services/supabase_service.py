import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.config.settings import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger("devflow.services.supabase")


def get_utc_now():
    return datetime.now(timezone.utc).isoformat()


class SupabaseService:
    def __init__(self):
        self.client = None
        self._is_enabled = False
        self._local_history: Dict[str, List[Dict[str, Any]]] = {}

        if (
            SUPABASE_URL
            and SUPABASE_KEY
            and SUPABASE_URL != "YOUR_SUPABASE_URL"
            and SUPABASE_KEY != "YOUR_SUPABASE_KEY"
        ):
            try:
                from supabase import create_client
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                self._is_enabled = True
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}. Falling back to in-memory store.")
        else:
            logger.info("Supabase credentials not configured. Running in local/in-memory mode.")

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    def save_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Saves project record to Supabase or local store."""
        if self._is_enabled and self.client:
            try:
                data = {
                    "id": project.get("id"),
                    "name": project.get("name"),
                    "description": project.get("description", ""),
                    "status": project.get("status", "NEW"),
                    "health_score": project.get("health_score"),
                    "file_count": project.get("file_count", 0),
                    "created_at": project.get("created_at", get_utc_now()),
                    "updated_at": project.get("updated_at", get_utc_now())
                }
                res = self.client.table("projects").upsert(data).execute()
                return res.data[0] if res.data else project
            except Exception as e:
                logger.error(f"Supabase save_project error: {e}")
        return project

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves project record from Supabase."""
        if self._is_enabled and self.client:
            try:
                res = self.client.table("projects").select("*").eq("id", project_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase get_project error: {e}")
        return None

    def list_projects(self) -> List[Dict[str, Any]]:
        """Retrieves all projects from Supabase ordered by updated_at desc."""
        if self._is_enabled and self.client:
            try:
                res = self.client.table("projects").select("*").order("updated_at", desc=True).execute()
                if res.data:
                    return res.data
            except Exception as e:
                logger.error(f"Supabase list_projects error: {e}")
        return []

    def save_analysis(self, project_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Saves analysis record."""
        if self._is_enabled and self.client:
            try:
                data = {
                    "project_id": project_id,
                    "summary": analysis.get("summary", ""),
                    "health_score": analysis.get("health_score", 0),
                    "created_at": get_utc_now()
                }
                res = self.client.table("analyses").insert(data).execute()
                record = res.data[0] if res.data else data

                # Save individual issues if table exists
                analysis_id = record.get("id")
                for issue in analysis.get("issues", []):
                    self.save_issue(analysis_id, issue)

                return record
            except Exception as e:
                logger.error(f"Supabase save_analysis error: {e}")

        # Local history fallback
        if project_id not in self._local_history:
            self._local_history[project_id] = []
        self._local_history[project_id].append({
            "type": "analysis",
            "data": analysis,
            "timestamp": get_utc_now()
        })
        return analysis

    def save_issue(self, analysis_id: Optional[str], issue: Dict[str, Any]) -> Dict[str, Any]:
        """Saves an issue linked to an analysis."""
        if self._is_enabled and self.client and analysis_id:
            try:
                data = {
                    "analysis_id": analysis_id,
                    "issue_code": issue.get("id"),
                    "title": issue.get("title"),
                    "category": issue.get("category"),
                    "severity": issue.get("severity"),
                    "file_path": issue.get("file"),
                    "line_number": issue.get("line"),
                    "description": issue.get("description"),
                    "impact": issue.get("impact"),
                    "recommendation": issue.get("recommendation"),
                }
                res = self.client.table("issues").insert(data).execute()
                return res.data[0] if res.data else issue
            except Exception as e:
                logger.error(f"Supabase save_issue error: {e}")
        return issue

    def save_fix(self, issue_id: str, fix_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Saves generated fix plan."""
        if self._is_enabled and self.client:
            try:
                data = {
                    "issue_id": issue_id,
                    "root_cause": fix_plan.get("root_cause"),
                    "files_to_change": fix_plan.get("files_to_change", []),
                    "implementation_steps": fix_plan.get("implementation_steps", []),
                    "regression_tests": fix_plan.get("regression_tests", []),
                    "code_diff": fix_plan.get("code_diff", ""),
                    "created_at": get_utc_now()
                }
                res = self.client.table("fixes").insert(data).execute()
                return res.data[0] if res.data else fix_plan
            except Exception as e:
                logger.error(f"Supabase save_fix error: {e}")
        return fix_plan

    def save_verification(self, project_id: str, verification: Dict[str, Any]) -> Dict[str, Any]:
        """Saves AST verification result."""
        if self._is_enabled and self.client:
            try:
                data = {
                    "project_id": project_id,
                    "passed": verification.get("passed", False),
                    "total_files": verification.get("total_files", 0),
                    "failed_files": verification.get("failed_files", []),
                    "verified_at": get_utc_now()
                }
                res = self.client.table("verification_results").insert(data).execute()
                return res.data[0] if res.data else verification
            except Exception as e:
                logger.error(f"Supabase save_verification error: {e}")
        return verification

    def get_project_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Retrieves history of analyses and verifications for a project."""
        if self._is_enabled and self.client:
            try:
                res = self.client.table("analyses").select("*").eq("project_id", project_id).order("created_at", desc=True).execute()
                return res.data
            except Exception as e:
                logger.error(f"Supabase get_project_history error: {e}")
        return self._local_history.get(project_id, [])


supabase_service = SupabaseService()
