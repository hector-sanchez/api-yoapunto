from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr  # Add EmailStr import
from app.crud.account import get_account_by_email
from app.models.account import Account
from app.auth_helper import create_access_token, pwd_context
from database import get_db

router = APIRouter()


class LoginRequest(BaseModel):
    email_address: EmailStr  # Change from str to EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse, tags=["auth"])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    account: Account = get_account_by_email(db, request.email_address)
    if not account or not account.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if not pwd_context.verify(request.password, account.password_digest):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token({"sub": account.id})
    return TokenResponse(access_token=token)


@router.post("/logout", tags=["auth"])
def logout(response: Response):
    """
    Placeholder logout endpoint. With JWT, logout is handled client-side.
    """
    response.status_code = status.HTTP_204_NO_CONTENT
    return
