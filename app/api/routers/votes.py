from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.vote import VoteCreate, VoteRead, VoteUpdate
from app.crud import votes as crud

router = APIRouter(prefix="/votes", tags=["votes"], dependencies=[Depends(verify_auth)])


@router.post("", response_model=VoteRead, status_code=status.HTTP_201_CREATED)
def create_vote(vote_in: VoteCreate, db: Session = Depends(get_db)) -> VoteRead:
    return crud.create_vote(db, vote_in)


@router.get("/{vote_id}", response_model=VoteRead)
def get_vote(vote_id: str, db: Session = Depends(get_db)) -> VoteRead:
    vote = crud.get_vote(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    return vote


@router.get("", response_model=List[VoteRead])
def list_votes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    project_id: str | None = Query(None),
    user_id: str | None = Query(None),
    db: Session = Depends(get_db)
) -> List[VoteRead]:
    if project_id:
        return list(crud.list_votes_by_project(db, project_id, skip=skip, limit=limit))
    if user_id:
        return list(crud.list_votes_by_user(db, user_id, skip=skip, limit=limit))
    return list(crud.list_votes(db, skip=skip, limit=limit))


@router.patch("/{vote_id}", response_model=VoteRead)
def update_vote(
    vote_id: str,
    vote_in: VoteUpdate,
    db: Session = Depends(get_db)
) -> VoteRead:
    return crud.update_vote(db, vote_id, vote_in)


@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vote(vote_id: str, db: Session = Depends(get_db)) -> None:
    crud.delete_vote(db, vote_id)
    return None
