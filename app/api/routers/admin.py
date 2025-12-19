from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from pydantic import BaseModel
from app.api.deps import get_db, verify_auth, verify_admin
from app.models.project import Project
from app.models.user import User
from app.models.onboarding_event import OnboardingEvent
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_auth), Depends(verify_admin)])


class ReviewUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    total_projects = db.query(func.count(Project.project_id)).scalar() or 0
    projects_this_week = db.query(func.count(Project.project_id)).filter(
        Project.created_at >= week_ago
    ).scalar() or 0
    shipped_projects = db.query(func.count(Project.project_id)).filter(
        Project.shipped == True
    ).scalar() or 0
    unshipped_projects = db.query(func.count(Project.project_id)).filter(
        Project.shipped == False
    ).scalar() or 0
    pending_review = db.query(func.count(Project.project_id)).filter(
        Project.review_status == "pending"
    ).scalar() or 0
    approved_projects = db.query(func.count(Project.project_id)).filter(
        Project.review_status == "approved"
    ).scalar() or 0
    rejected_projects = db.query(func.count(Project.project_id)).filter(
        Project.review_status == "rejected"
    ).scalar() or 0
    flagged_projects = db.query(func.count(Project.project_id)).filter(
        Project.review_status == "flagged"
    ).scalar() or 0

    total_users = db.query(func.count(User.user_id)).scalar() or 0
    users_with_projects = db.query(func.count(func.distinct(Project.user_id))).scalar() or 0
    new_users_this_week = db.query(func.count(User.user_id)).filter(
        User.created_at >= week_ago
    ).scalar() or 0
    onboarding_completed = db.query(func.count(User.user_id)).filter(
        User.onboarding_completed_at.isnot(None)
    ).scalar() or 0

    total_hours = db.query(func.coalesce(func.sum(Project.hackatime_hours), 0.0)).scalar() or 0.0
    hours_this_week = db.query(func.coalesce(func.sum(Project.hackatime_hours), 0.0)).filter(
        Project.created_at >= week_ago
    ).scalar() or 0.0
    projects_with_no_hours = db.query(func.count(Project.project_id)).filter(
        or_(Project.hackatime_hours == 0, Project.hackatime_hours.is_(None))
    ).scalar() or 0
    projects_with_high_hours = db.query(func.count(Project.project_id)).filter(
        Project.hackatime_hours > 80
    ).scalar() or 0

    onboarding_starts_total = db.query(func.count(func.distinct(OnboardingEvent.user_id))).filter(
        OnboardingEvent.event == "start"
    ).scalar() or 0
    onboarding_completions_total = db.query(func.count(func.distinct(OnboardingEvent.user_id))).filter(
        OnboardingEvent.event == "complete"
    ).scalar() or 0
    onboarding_starts_7d = db.query(func.count(func.distinct(OnboardingEvent.user_id))).filter(
        OnboardingEvent.event == "start",
        OnboardingEvent.created_at >= week_ago
    ).scalar() or 0
    onboarding_completions_7d = db.query(func.count(func.distinct(OnboardingEvent.user_id))).filter(
        OnboardingEvent.event == "complete",
        OnboardingEvent.created_at >= week_ago
    ).scalar() or 0

    return {
        "projects": {
            "total": total_projects,
            "this_week": projects_this_week,
            "shipped": shipped_projects,
            "unshipped": unshipped_projects,
            "pending_review": pending_review,
            "approved": approved_projects,
            "rejected": rejected_projects,
            "flagged": flagged_projects
        },
        "users": {
            "total": total_users,
            "with_projects": users_with_projects,
            "new_this_week": new_users_this_week,
            "onboarding_completed": onboarding_completed
        },
        "hackatime": {
            "total_hours": float(total_hours),
            "hours_this_week": float(hours_this_week),
            "projects_with_no_hours": projects_with_no_hours,
            "projects_with_high_hours": projects_with_high_hours
        },
        "onboarding": {
            "starts_total": onboarding_starts_total,
            "completions_total": onboarding_completions_total,
            "starts_last_7d": onboarding_starts_7d,
            "completions_last_7d": onboarding_completions_7d
        }
    }


@router.get("/projects")
def list_projects(
    q: Optional[str] = Query(None),
    week: Optional[str] = Query(None),
    shipped: Optional[bool] = Query(None),
    review_status: Optional[str] = Query(None),
    min_hours: Optional[float] = Query(None),
    max_hours: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> list[dict]:
    query = db.query(Project).join(User, Project.user_id == User.user_id)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                Project.project_name.ilike(search),
                User.handle.ilike(search)
            )
        )
    if week:
        query = query.filter(Project.submission_week == week)
    if shipped is not None:
        query = query.filter(Project.shipped == shipped)
    if review_status:
        query = query.filter(Project.review_status == review_status)
    if min_hours is not None:
        query = query.filter(Project.hackatime_hours >= min_hours)
    if max_hours is not None:
        query = query.filter(Project.hackatime_hours <= max_hours)

    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "project_id": p.project_id,
            "project_name": p.project_name,
            "project_description": p.project_description,
            "project_type": p.project_type,
            "submission_week": p.submission_week,
            "shipped": p.shipped,
            "hackatime_hours": p.hackatime_hours,
            "review_status": p.review_status,
            "review_notes": p.review_notes,
            "reviewed_by": p.reviewed_by,
            "reviewed_at": p.reviewed_at.isoformat() if p.reviewed_at else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "user": {
                "user_id": p.user.user_id,
                "handle": p.user.handle,
                "email": p.user.email
            }
        }
        for p in projects
    ]


@router.get("/users")
def list_users(
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> list[dict]:
    query = db.query(User)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                User.handle.ilike(search),
                User.user_id.ilike(search),
                User.email.ilike(search)
            )
        )

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    project_counts = dict(
        db.query(Project.user_id, func.count(Project.project_id))
        .filter(Project.user_id.in_([u.user_id for u in users]))
        .group_by(Project.user_id)
        .all()
    )

    return [
        {
            "user_id": u.user_id,
            "handle": u.handle,
            "email": u.email,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "onboarding_completed_at": u.onboarding_completed_at.isoformat() if u.onboarding_completed_at else None,
            "project_count": project_counts.get(u.user_id, 0)
        }
        for u in users
    ]


@router.post("/projects/{project_id}/review")
def update_project_review(
    project_id: str,
    body: ReviewUpdateRequest,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> dict:
    if body.status not in ["approved", "rejected", "flagged", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be one of: approved, rejected, flagged, pending")

    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    old_status = project.review_status
    project.review_status = body.status
    project.review_notes = body.notes
    project.reviewed_by = x_user_id
    project.reviewed_at = datetime.now(timezone.utc)

    audit_log = AuditLog(
        user_id=x_user_id,
        object_type="project",
        object_id=project_id,
        action="review_status_update",
        details={
            "old_status": old_status,
            "new_status": body.status,
            "notes": body.notes
        }
    )
    db.add(audit_log)
    db.commit()

    return {
        "message": "Review status updated",
        "project_id": project_id,
        "review_status": body.status,
        "reviewed_by": x_user_id,
        "reviewed_at": project.reviewed_at.isoformat()
    }


@router.get("/projects/anomalies")
def get_projects_with_anomalies(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> list[dict]:
    projects = db.query(Project).join(User, Project.user_id == User.user_id).filter(
        or_(
            Project.hackatime_hours == 0,
            Project.hackatime_hours > 80,
            Project.hackatime_hours.is_(None)
        )
    ).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    def get_anomaly_type(hours):
        if hours is None:
            return "null_hours"
        elif hours == 0:
            return "zero_hours"
        elif hours > 80:
            return "high_hours"
        return "unknown"

    return [
        {
            "project_id": p.project_id,
            "project_name": p.project_name,
            "submission_week": p.submission_week,
            "shipped": p.shipped,
            "hackatime_hours": p.hackatime_hours,
            "review_status": p.review_status,
            "anomaly_type": get_anomaly_type(p.hackatime_hours),
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "user": {
                "user_id": p.user.user_id,
                "handle": p.user.handle
            }
        }
        for p in projects
    ]
