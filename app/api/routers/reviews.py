from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth, verify_admin
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.crud import reviews as crud

router = APIRouter(prefix="/reviews", tags=["reviews"], dependencies=[Depends(verify_auth)])


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin)])
def create_review(review_in: ReviewCreate, db: Session = Depends(get_db)) -> ReviewRead:
    return crud.create_review(db, review_in)


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: str, db: Session = Depends(get_db)) -> ReviewRead:
    review = crud.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("", response_model=List[ReviewRead])
def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    project_id: str | None = Query(None),
    reviewer_user_id: str | None = Query(None),
    db: Session = Depends(get_db)
) -> List[ReviewRead]:
    if project_id:
        return list(crud.list_reviews_by_project(db, project_id, skip=skip, limit=limit))
    if reviewer_user_id:
        return list(crud.list_reviews_by_reviewer(db, reviewer_user_id, skip=skip, limit=limit))
    return list(crud.list_reviews(db, skip=skip, limit=limit))


@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: str,
    review_in: ReviewUpdate,
    db: Session = Depends(get_db)
) -> ReviewRead:
    return crud.update_review(db, review_id, review_in)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: str, db: Session = Depends(get_db)) -> None:
    crud.delete_review(db, review_id)
    return None
