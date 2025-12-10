from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException, Header
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_auth
from app.schemas.vote import VoteCreate, VoteRead, VoteUpdate
from app.crud import votes as crud
from app.crud import users as users_crud

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
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> VoteRead:
    """
    Update a vote.
    
    SECURITY: Ownership check - users can only update their own votes.
    Without this, any authenticated user could change anyone's vote (IDOR vulnerability).
    Admins can update any vote.
    """
    vote = crud.get_vote(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    requesting_user = users_crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    
    # Ownership check: only the user who cast the vote OR an admin can update
    is_admin = users_crud.has_role(db, x_user_id, "admin")
    if vote.user_id != x_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own votes"
        )

    return crud.update_vote(db, vote_id, vote_in)


@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vote(
    vote_id: str,
    x_user_id: str = Header(...),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a vote.
    
    SECURITY: Ownership check - users can only delete their own votes.
    Without this, any authenticated user could delete anyone's vote (IDOR vulnerability).
    Admins can delete any vote.
    """
    vote = crud.get_vote(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    requesting_user = users_crud.get_user(db, x_user_id)
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    
    # Ownership check: only the user who cast the vote OR an admin can delete
    is_admin = users_crud.has_role(db, x_user_id, "admin")
    if vote.user_id != x_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own votes"
        )

    crud.delete_vote(db, vote_id)
    return None
