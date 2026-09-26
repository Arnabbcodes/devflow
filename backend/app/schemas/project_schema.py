from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def get_utc_now():
    return datetime.now(timezone.utc).isoformat()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    status: str = "UPLOADED"  # UPLOADED, ANALYZED, VERIFIED, READY
    health_score: Optional[int] = None
    file_count: int = 0
    project_text: Optional[str] = None
    created_at: str = Field(default_factory=get_utc_now)
    updated_at: str = Field(default_factory=get_utc_now)


class ProjectResponse(BaseModel):
    success: bool
    message: str
    project: Project


class ProjectListResponse(BaseModel):
    success: bool
    count: int
    projects: List[Project]
