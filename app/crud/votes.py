from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.vote import Vote
from app.schemas.vote import VoteCreate, VoteUpdate


def create_vote(db: Session, data: VoteCreate) -> Vote:
    vote = Vote(**data.model_dump())
    db.add(vote)
    try:
        db.commit()
        db.refresh(vote)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id or project_id or database constraint violation"
        )
    return vote


def get_vote(db: Session, vote_id: str) -> Vote | None:
    return db.get(Vote, vote_id)


def list_votes(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Vote]:
    return db.query(Vote).offset(skip).limit(limit).all()


def list_votes_by_project(db: Session, project_id: str, skip: int = 0, limit: int = 100) -> Sequence[Vote]:
    return db.query(Vote).filter(Vote.project_id == project_id).offset(skip).limit(limit).all()


def list_votes_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[Vote]:
    return db.query(Vote).filter(Vote.user_id == user_id).offset(skip).limit(limit).all()


def update_vote(db: Session, vote_id: str, data: VoteUpdate) -> Vote:
    vote = get_vote(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(vote, k, v)
    
    try:
        db.commit()
        db.refresh(vote)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database constraint violation"
        )
    return vote


def delete_vote(db: Session, vote_id: str) -> None:
    vote = get_vote(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    db.delete(vote)
    db.commit()
