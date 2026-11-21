"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.db.session import get_db
from app.models.entities import Role, User
from app.schemas.auth import CurrentUserResponse, LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=CurrentUserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.email == request.email.lower())):
        raise HTTPException(status_code=409, detail="Email is already registered")
    role = db.scalar(select(Role).where(Role.name == "analyst"))
    if role is None:
        role = Role(name="analyst", description="Standard legal document analyst")
        db.add(role)
        db.flush()
    user = User(email=request.email.lower(), full_name=request.full_name, password_hash=hash_password(request.password), role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == request.email.lower()))
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    try:
        token = create_access_token(user.id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication is not configured") from exc
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserResponse)
def current_user(user: User = Depends(get_current_user)) -> User:
    return user
