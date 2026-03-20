from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from bimba3d_backend.app.config import APP_MODE, DB_ENABLED
from bimba3d_backend.app.services.db import ProjectRecord, User, db_session
from bimba3d_backend.app.services.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _assert_admin_enabled() -> None:
    if APP_MODE != "server" or not DB_ENABLED:
        raise HTTPException(status_code=503, detail="Admin API disabled (set APP_MODE=server and DB_ENABLED=true)")


@router.get("/users")
def list_users(_: dict = Depends(require_admin)):
    _assert_admin_enabled()
    with db_session() as session:
        users = session.execute(select(User).order_by(User.created_at.desc())).scalars().all()
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]


@router.get("/projects")
def list_project_records(_: dict = Depends(require_admin)):
    _assert_admin_enabled()
    with db_session() as session:
        projects = session.execute(select(ProjectRecord).order_by(ProjectRecord.created_at.desc())).scalars().all()
        return [
            {
                "project_id": project.project_id,
                "owner_user_id": project.owner_user_id,
                "name": project.name,
                "description": project.description,
                "video_url": project.video_url,
                "category": project.category,
                "visibility": project.visibility,
                "created_at": project.created_at.isoformat() if project.created_at else None,
            }
            for project in projects
        ]
