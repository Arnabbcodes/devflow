import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.services.supabase_service import supabase_service


def get_utc_now():
    return datetime.now(timezone.utc).isoformat()


class ProjectService:
    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
        self._seed_default_projects()

    def _seed_default_projects(self):
        """Seeds initial mock project records matching Flutter frontend dashboard."""
        now = get_utc_now()
        seeds = [
            {
                "id": "demo-project-001",
                "name": "demo-project",
                "description": "Intentionally vulnerable sample API for DevFlow evaluation",
                "status": "READY",
                "health_score": 61,
                "file_count": 4,
                "project_text": None,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "todo-api-002",
                "name": "Todo API",
                "description": "FastAPI REST API with PostgreSQL backend",
                "status": "ANALYZED",
                "health_score": 85,
                "file_count": 8,
                "project_text": None,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "student-portal-003",
                "name": "Student Portal",
                "description": "Django web application for course registration",
                "status": "ANALYZED",
                "health_score": 72,
                "file_count": 14,
                "project_text": None,
                "created_at": now,
                "updated_at": now,
            }
        ]
        for p in seeds:
            self.projects[p["id"]] = p

    def create_project(
        self,
        name: str,
        project_text: Optional[str] = None,
        description: str = "",
        file_count: int = 0,
        directory_path: Optional[str] = None,
        custom_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new project and stores in memory + Supabase."""
        project_id = custom_id or str(uuid.uuid4())[:8]
        now = get_utc_now()

        project_record = {
            "id": project_id,
            "name": name,
            "description": description,
            "status": "UPLOADED",
            "health_score": None,
            "file_count": file_count,
            "project_text": project_text,
            "directory_path": directory_path,
            "created_at": now,
            "updated_at": now,
        }

        self.projects[project_id] = project_record
        supabase_service.save_project(project_record)
        return project_record

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a project by ID."""
        if project_id in self.projects:
            return self.projects[project_id]
        if supabase_service.is_enabled:
            remote_proj = supabase_service.get_project(project_id)
            if remote_proj:
                self.projects[project_id] = remote_proj
                return remote_proj
        return None

    def list_projects(self) -> List[Dict[str, Any]]:
        """Lists all projects ordered by updated_at desc."""
        if supabase_service.is_enabled:
            remote_projects = supabase_service.list_projects()
            if remote_projects:
                for p in remote_projects:
                    self.projects[p["id"]] = p
        return sorted(
            list(self.projects.values()),
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Updates project fields."""
        if project_id not in self.projects:
            return None

        self.projects[project_id].update(updates)
        self.projects[project_id]["updated_at"] = get_utc_now()
        supabase_service.save_project(self.projects[project_id])
        return self.projects[project_id]


project_service = ProjectService()
