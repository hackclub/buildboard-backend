"""
Submission service with midnight-style validation.
Validates all requirements before allowing a project to be shipped.
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_address import UserAddress

AGE_LIMIT = 19


@dataclass
class ValidationError:
    field: str
    message: str


@dataclass
class SubmissionValidationResult:
    valid: bool
    errors: list[ValidationError]


def _calculate_age(birthday: datetime) -> int:
    today = datetime.now(timezone.utc)
    age = today.year - birthday.year
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1
    return age


def validate_submission(db: Session, project: Project, user: User) -> SubmissionValidationResult:
    """
    Validate all requirements for project submission.
    Mirrors midnight's validation:
    1. Age must be under 19
    2. User profile must be complete (first name, birthday)
    3. User must have an address
    4. Hackatime must be linked with at least one project
    5. Project must have all required fields (repo URL, live URL, screenshot)
    """
    errors: list[ValidationError] = []

    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.user_id).first()

    # 1. Check user profile exists and has required fields
    if not profile:
        errors.append(ValidationError(
            field="profile",
            message="User profile is required. Please complete your profile."
        ))
    else:
        if not profile.first_name or not profile.first_name.strip():
            errors.append(ValidationError(
                field="first_name",
                message="First name is required."
            ))

        # 2. Check birthday and age
        if not profile.birthday:
            errors.append(ValidationError(
                field="birthday",
                message="Birthday is required."
            ))
        else:
            age = _calculate_age(profile.birthday)
            if age >= AGE_LIMIT:
                errors.append(ValidationError(
                    field="age",
                    message=f"You must be under {AGE_LIMIT} years old to submit."
                ))

    # 3. Check address
    address = db.query(UserAddress).filter(
        UserAddress.user_id == user.user_id,
        UserAddress.is_primary == True
    ).first()

    if not address:
        errors.append(ValidationError(
            field="address",
            message="A shipping address is required."
        ))
    else:
        if not address.address_line_1 or not address.address_line_1.strip():
            errors.append(ValidationError(
                field="address_line_1",
                message="Address line 1 is required."
            ))
        if not address.city or not address.city.strip():
            errors.append(ValidationError(
                field="city",
                message="City is required."
            ))
        if not address.country or not address.country.strip():
            errors.append(ValidationError(
                field="country",
                message="Country is required."
            ))
        if not address.post_code or not address.post_code.strip():
            errors.append(ValidationError(
                field="post_code",
                message="Post/ZIP code is required."
            ))

    # 4. Check Hackatime projects linked
    if not project.hackatime_projects or len(project.hackatime_projects) == 0:
        errors.append(ValidationError(
            field="hackatime_projects",
            message="At least one Hackatime project must be linked."
        ))

    # 5. Check project required fields
    if not project.code_url and not project.github_repo_path:
        errors.append(ValidationError(
            field="code_url",
            message="A GitHub repository URL is required."
        ))

    if not project.live_url:
        errors.append(ValidationError(
            field="live_url",
            message="A live/playable project URL is required."
        ))

    if not project.attachment_urls or len(project.attachment_urls) == 0:
        errors.append(ValidationError(
            field="screenshot",
            message="At least one screenshot is required."
        ))

    return SubmissionValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )


def submit_project(db: Session, project: Project, user: User) -> tuple[Project, SubmissionValidationResult]:
    """
    Validate and submit a project.
    Returns the updated project and validation result.
    """
    validation = validate_submission(db, project, user)

    if not validation.valid:
        return project, validation

    # Mark as shipped
    project.shipped = True
    db.commit()
    db.refresh(project)

    return project, validation
