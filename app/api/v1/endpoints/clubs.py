from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import Club, ClubCreate, ClubUpdate
from app.crud.club import create_club, get_clubs, get_club, update_club, deactivate_club
from database import get_db

router = APIRouter()

@router.post("/", response_model=Club)
def create_club_endpoint(club: ClubCreate, db: Session = Depends(get_db)):
    return create_club(db=db, club=club)

@router.get("/", response_model=List[Club])
def read_clubs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_clubs(db=db, skip=skip, limit=limit)

@router.get("/{club_id}", response_model=Club)
def read_club(club_id: int, db: Session = Depends(get_db)):
    club = get_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    return club

@router.put("/{club_id}", response_model=Club)
def update_club_endpoint(club_id: int, club: ClubUpdate, db: Session = Depends(get_db)):
    updated_club = update_club(db=db, club_id=club_id, club=club)
    if updated_club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    return updated_club

@router.delete("/{club_id}")
def delete_club(club_id: int, db: Session = Depends(get_db)):
    club = deactivate_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    return {"message": "Club deactivated successfully"}
