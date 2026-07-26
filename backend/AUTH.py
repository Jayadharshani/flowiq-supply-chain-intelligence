from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
 
from database import get_db
from DB_models import User
 
# ==========================================================
# CONFIG
# ==========================================================
# SECRET_KEY signs every token - anyone with this key could forge
# valid login tokens, so it must stay private and never be committed
# to GitHub. For real deployment, this should come from an
# environment variable instead of being hardcoded like this.
import os
 
# SECRET_KEY signs every token - anyone with this key could forge
# valid login tokens, so it must stay private. On Render, this comes
# from the SECRET_KEY environment variable you set in the dashboard.
# Locally, it falls back to a dev-only placeholder - fine for testing
# on your own machine, but never use this fallback value in production.
SECRET_KEY = os.environ.get("SECRET_KEY", "flowiq-dev-secret-change-this-before-deploying")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # tokens stay valid for 24 hours
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
# Tells FastAPI where the frontend should send username/password to
# get a token - used for the auto-generated /docs "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
 
 
# ==========================================================
# PASSWORD HASHING
# ==========================================================
 
def hash_password(password: str) -> str:
    """One-way scramble - cannot be reversed back to the original."""
    return pwd_context.hash(password)
 
 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Hashes the login attempt and compares hashes - never compares raw text."""
    return pwd_context.verify(plain_password, hashed_password)
 
 
# ==========================================================
# JWT TOKEN CREATION
# ==========================================================
 
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 
 
# ==========================================================
# DEPENDENCY: GET THE CURRENTLY LOGGED-IN USER
# ==========================================================
# FastAPI runs this automatically for any endpoint that declares
# `current_user: User = Depends(get_current_user)`. It reads the
# token from the request, verifies it's genuine and unexpired,
# and looks up the matching user - or rejects the request with 401.
 
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
 
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
 