from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


def create_review(db: Session, data: ReviewCreate) -> Review:
    review = Review(**data.model_dump())
    db.add(review)
    try:
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reviewer_user_id or project_id or database constraint violation"
        )
    return review


def get_review(db: Session, review_id: str) -> Review | None:
    return db.get(Review, review_id)


def list_reviews(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Review]:
    return db.query(Review).offset(skip).limit(limit).all()


def list_reviews_by_project(db: Session, project_id: str, skip: int = 0, limit: int = 100) -> Sequence[Review]:
    return db.query(Review).filter(Review.project_id == project_id).offset(skip).limit(limit).all()


def list_reviews_by_reviewer(db: Session, reviewer_user_id: str, skip: int = 0, limit: int = 100) -> Sequence[Review]:
    return db.query(Review).filter(Review.reviewer_user_id == reviewer_user_id).offset(skip).limit(limit).all()


def update_review(db: Session, review_id: str, data: ReviewUpdate) -> Review:
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(review, k, v)
    
    try:
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database constraint violation"
        )
    return review


def delete_review(db: Session, review_id: str) -> None:
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
