from sqlalchemy.orm import Session
from app.models import Club
from app.schemas import ClubCreate, ClubUpdate

def create_club(db: Session, club: ClubCreate):
    db_club = Club(**club.model_dump())
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club

def get_clubs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Club).filter(Club.active == True).offset(skip).limit(limit).all()

def get_club(db: Session, club_id: int):
    return db.query(Club).filter(Club.id == club_id, Club.active == True).first()

def update_club(db: Session, club_id: int, club: ClubUpdate):
    db_club = db.query(Club).filter(Club.id == club_id, Club.active == True).first()
    if db_club is None:
        return None

    update_data = club.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_club, field, value)

    db.commit()
    db.refresh(db_club)
    return db_club

def deactivate_club(db: Session, club_id: int):
    db_club = db.query(Club).filter(Club.id == club_id, Club.active == True).first()
    if db_club is None:
        return None

    db_club.active = False
    db.commit()
    return db_club
