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
from app.models.hackatime_project import HackatimeProject
from app.models.user_login_event import UserLoginEvent
from app.models.vote import Vote
from app.models.review import Review

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

    # User journey funnel - count users at each milestone
    slack_linked = db.query(func.count(User.user_id)).filter(
        User.slack_id.isnot(None)
    ).scalar() or 0
    idv_completed = db.query(func.count(User.user_id)).filter(
        User.idv_completed_at.isnot(None)
    ).scalar() or 0
    hackatime_completed = db.query(func.count(User.user_id)).filter(
        User.hackatime_completed_at.isnot(None)
    ).scalar() or 0

    # Users who have shipped at least one project
    users_with_shipped = db.query(func.count(func.distinct(Project.user_id))).filter(
        Project.shipped == True
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
        },
        "user_journey": {
            "total_users": total_users,
            "slack_linked": slack_linked,
            "idv_completed": idv_completed,
            "hackatime_completed": hackatime_completed,
            "onboarding_completed": onboarding_completed,
            "has_projects": users_with_projects,
            "has_shipped": users_with_shipped
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

    def get_journey_step(user: User) -> dict:
        steps = [
            ("registered", True),
            ("slack", user.slack_id is not None),
            ("idv", user.idv_completed_at is not None),
            ("hackatime", user.hackatime_completed_at is not None),
            ("onboarding", user.onboarding_completed_at is not None),
        ]
        completed = sum(1 for _, done in steps if done)
        current_step = "registered"
        for step_name, done in steps:
            if done:
                current_step = step_name
            else:
                break
        return {
            "current_step": current_step,
            "completed_count": completed,
            "total_steps": len(steps),
            "slack": user.slack_id is not None,
            "idv": user.idv_completed_at is not None,
            "hackatime": user.hackatime_completed_at is not None,
            "onboarding": user.onboarding_completed_at is not None,
        }

    return [
        {
            "user_id": u.user_id,
            "handle": u.handle,
            "email": u.email,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "onboarding_completed_at": u.onboarding_completed_at.isoformat() if u.onboarding_completed_at else None,
            "project_count": project_counts.get(u.user_id, 0),
            "journey": get_journey_step(u)
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


@router.get("/users/{user_id}")
def get_user_detail(
    user_id: str,
    db: Session = Depends(get_db)
) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's projects with details
    projects = db.query(Project).filter(Project.user_id == user_id).order_by(Project.created_at.desc()).all()
    
    # Calculate total hackatime hours across all projects
    total_hours = sum(p.hackatime_hours or 0 for p in projects)
    shipped_count = sum(1 for p in projects if p.shipped)
    
    # Get hackatime projects
    hackatime_projects = db.query(HackatimeProject).filter(
        HackatimeProject.user_id == user_id
    ).order_by(HackatimeProject.seconds.desc()).all()
    total_hackatime_seconds = sum(hp.seconds for hp in hackatime_projects)
    
    # Get login events (last 10)
    login_events = db.query(UserLoginEvent).filter(
        UserLoginEvent.user_id == user_id
    ).order_by(UserLoginEvent.logged_in_at.desc()).limit(10).all()
    
    # Get votes cast by this user
    votes_cast = db.query(func.count(Vote.vote_id)).filter(Vote.user_id == user_id).scalar() or 0
    
    # Get votes received on user's projects
    votes_received = db.query(func.count(Vote.vote_id)).filter(
        Vote.project_id.in_([p.project_id for p in projects])
    ).scalar() or 0 if projects else 0
    
    # Get reviews received on user's projects
    reviews_received = db.query(Review).filter(
        Review.project_id.in_([p.project_id for p in projects])
    ).all() if projects else []
    
    # Get onboarding events
    onboarding_events = db.query(OnboardingEvent).filter(
        OnboardingEvent.user_id == user_id
    ).order_by(OnboardingEvent.created_at.desc()).all()
    
    # Get audit logs for this user
    audit_logs = db.query(AuditLog).filter(
        AuditLog.object_id == user_id,
        AuditLog.object_type == "user"
    ).order_by(AuditLog.created_at.desc()).limit(20).all()
    
    # Get user roles
    roles = [ur.role.role_id for ur in user.roles] if user.roles else []
    
    # Get referral info
    referred_users_count = db.query(func.count(User.user_id)).filter(
        User.referred_by_user_id == user_id
    ).scalar() or 0
    
    referrer = None
    if user.referred_by_user_id:
        ref_user = db.get(User, user.referred_by_user_id)
        if ref_user:
            referrer = {"user_id": ref_user.user_id, "handle": ref_user.handle}

    # Build journey status
    journey = {
        "slack": {"completed": user.slack_id is not None, "slack_id": user.slack_id},
        "idv": {"completed": user.idv_completed_at is not None, "completed_at": user.idv_completed_at.isoformat() if user.idv_completed_at else None},
        "hackatime": {"completed": user.hackatime_completed_at is not None, "completed_at": user.hackatime_completed_at.isoformat() if user.hackatime_completed_at else None},
        "onboarding": {"completed": user.onboarding_completed_at is not None, "completed_at": user.onboarding_completed_at.isoformat() if user.onboarding_completed_at else None},
    }

    return {
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "handle": user.handle,
            "slack_id": user.slack_id,
            "phone_number": user.phone_number,
            "referral_code": user.referral_code,
            "identity_vault_id": user.identity_vault_id,
            "idv_country": user.idv_country,
            "verification_status": user.verification_status,
            "ysws_eligible": user.ysws_eligible,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        },
        "profile": {
            "first_name": user.profile.first_name if user.profile else None,
            "last_name": user.profile.last_name if user.profile else None,
            "avatar_url": user.profile.avatar_url if user.profile else None,
            "bio": user.profile.bio if user.profile else None,
            "is_public": user.profile.is_public if user.profile else False,
            "birthday": user.profile.birthday.isoformat() if user.profile and user.profile.birthday else None,
        },
        "journey": journey,
        "roles": roles,
        "stats": {
            "total_projects": len(projects),
            "shipped_projects": shipped_count,
            "total_hours": total_hours,
            "total_hackatime_seconds": total_hackatime_seconds,
            "votes_cast": votes_cast,
            "votes_received": votes_received,
            "reviews_received": len(reviews_received),
            "login_count": len(login_events),
            "referred_users": referred_users_count,
        },
        "referrer": referrer,
        "projects": [
            {
                "project_id": p.project_id,
                "project_name": p.project_name,
                "project_description": p.project_description[:200] + "..." if p.project_description and len(p.project_description) > 200 else p.project_description,
                "project_type": p.project_type,
                "submission_week": p.submission_week,
                "shipped": p.shipped,
                "hackatime_hours": p.hackatime_hours,
                "review_status": p.review_status,
                "code_url": p.code_url,
                "live_url": p.live_url,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ],
        "hackatime_projects": [
            {
                "id": hp.id,
                "name": hp.name,
                "seconds": hp.seconds,
                "hours": round(hp.seconds / 3600, 2),
                "updated_at": hp.updated_at.isoformat() if hp.updated_at else None,
            }
            for hp in hackatime_projects
        ],
        "recent_logins": [
            {
                "id": le.id,
                "logged_in_at": le.logged_in_at.isoformat() if le.logged_in_at else None,
            }
            for le in login_events
        ],
        "onboarding_events": [
            {
                "id": oe.id,
                "event": oe.event,
                "slide": oe.slide,
                "created_at": oe.created_at.isoformat() if oe.created_at else None,
            }
            for oe in onboarding_events[:10]
        ],
        "audit_logs": [
            {
                "id": al.id,
                "action": al.action,
                "details": al.details,
                "created_at": al.created_at.isoformat() if al.created_at else None,
            }
            for al in audit_logs
        ],
    }
