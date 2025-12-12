from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.review import Review
from app.schemas.visibility import VisibilityLevel, VisibilityMilestone, VisibilityStatus

HOURS_THRESHOLD = 30.0

LEVEL_NAMES = {
    VisibilityLevel.HIDDEN: "Hidden",
    VisibilityLevel.LOCAL: "Local",
    VisibilityLevel.COMMUNITY: "Community",
    VisibilityLevel.FEATURED: "Featured",
    VisibilityLevel.BILLBOARD: "Billboard",
}


@dataclass
class VisibilityState:
    has_github: bool
    has_hackatime: bool
    is_shipped: bool
    is_approved: bool
    hackatime_hours: float
    has_enough_hours: bool

    @property
    def is_connected(self) -> bool:
        return self.has_github and self.has_hackatime


def _get_visibility_state(db: Session, project: Project) -> VisibilityState:
    # GitHub is linked if they have a code_url OR the GitHub App integration
    has_github = bool(project.code_url) or bool(project.github_repo_path)
    has_hackatime = bool(project.hackatime_projects and len(project.hackatime_projects) > 0)
    is_shipped = project.shipped
    hackatime_hours = project.hackatime_hours if project.hackatime_hours is not None else 0.0
    has_enough_hours = hackatime_hours >= HOURS_THRESHOLD

    approved_review = (
        db.query(Review)
        .filter(
            Review.project_id == project.project_id,
            Review.review_decision == "approved",
        )
        .first()
    )
    is_approved = approved_review is not None

    return VisibilityState(
        has_github=has_github,
        has_hackatime=has_hackatime,
        is_shipped=is_shipped,
        is_approved=is_approved,
        hackatime_hours=hackatime_hours,
        has_enough_hours=has_enough_hours,
    )


def _determine_level(state: VisibilityState) -> VisibilityLevel:
    connected = state.is_connected

    if connected and state.is_shipped and state.is_approved and state.has_enough_hours:
        return VisibilityLevel.BILLBOARD

    if connected and state.is_shipped and state.is_approved:
        return VisibilityLevel.FEATURED

    if connected and state.is_shipped:
        return VisibilityLevel.COMMUNITY

    if connected:
        return VisibilityLevel.LOCAL

    return VisibilityLevel.HIDDEN


def _get_milestones(state: VisibilityState) -> list[VisibilityMilestone]:
    is_billboard = (
        state.is_connected
        and state.is_shipped
        and state.is_approved
        and state.has_enough_hours
    )

    return [
        VisibilityMilestone(
            id="github",
            name="Link GitHub",
            description="Connect your GitHub repository",
            completed=state.has_github,
            level=VisibilityLevel.LOCAL,
        ),
        VisibilityMilestone(
            id="hackatime",
            name="Link Hackatime",
            description="Connect your Hackatime project to track hours",
            completed=state.has_hackatime,
            level=VisibilityLevel.LOCAL,
        ),
        VisibilityMilestone(
            id="shipped",
            name="Ship It",
            description="Mark your project as shipped",
            completed=state.is_shipped,
            level=VisibilityLevel.COMMUNITY,
        ),
        VisibilityMilestone(
            id="approved",
            name="Get Approved",
            description="Submit for admin review and get approved",
            completed=state.is_approved,
            level=VisibilityLevel.FEATURED,
        ),
        VisibilityMilestone(
            id="hours",
            name="Log 30+ Hours",
            description=f"Track at least {int(HOURS_THRESHOLD)} hours in Hackatime",
            completed=state.has_enough_hours,
            level=VisibilityLevel.BILLBOARD,
        ),
    ]


def _calculate_progress(milestones: list[VisibilityMilestone], state: VisibilityState) -> int:
    base_per_milestone = 100 / len(milestones)
    progress = 0.0

    for m in milestones:
        if m.id == "billboard":
            hours_fraction = min(state.hackatime_hours / HOURS_THRESHOLD, 1.0)
            progress += base_per_milestone * hours_fraction
        elif m.completed:
            progress += base_per_milestone

    return int(progress)


def calculate_visibility(db: Session, project: Project) -> VisibilityStatus:
    state = _get_visibility_state(db, project)
    milestones = _get_milestones(state)
    current_level = _determine_level(state)

    completed_count = sum(1 for m in milestones if m.completed)
    total_count = len(milestones)

    next_level = VisibilityLevel(current_level + 1) if current_level < VisibilityLevel.BILLBOARD else None

    progress = _calculate_progress(milestones, state)

    return VisibilityStatus(
        current_level=current_level,
        current_level_name=LEVEL_NAMES[current_level],
        next_level=next_level.value if next_level is not None else None,
        next_level_name=LEVEL_NAMES.get(next_level) if next_level is not None else None,
        progress_percentage=progress,
        milestones=milestones,
        total_completed=completed_count,
        total_milestones=total_count,
    )
