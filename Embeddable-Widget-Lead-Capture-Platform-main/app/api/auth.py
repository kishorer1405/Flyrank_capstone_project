from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
router=APIRouter(prefix="/api/v1/auth", tags=["auth"])
@router.post("/register",response_model=UserResponse,status_code=201)
def register(payload:RegisterRequest,db:Session=Depends(get_db)):
    if db.scalar(select(User).where(User.email==payload.email.lower())): raise HTTPException(409,"Email already registered")
    u=User(email=payload.email.lower(),password_hash=hash_password(payload.password),company_name=payload.company_name)
    db.add(u); db.commit(); db.refresh(u); return u
@router.post("/login",response_model=TokenResponse)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==form.username.lower()))
    if not u or not verify_password(form.password,u.password_hash): raise HTTPException(401,"Incorrect email or password",headers={"WWW-Authenticate":"Bearer"})
    return TokenResponse(access_token=create_access_token(str(u.id)))
@router.get("/me",response_model=UserResponse)
def me(user:User=Depends(get_current_user)): return user
