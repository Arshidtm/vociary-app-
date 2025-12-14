# backend/app/api/auth.py

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core import security
from ..core.settings import settings
from ..db.database import get_db_async
from ..db import models
from ..schemas import user as user_schemas
from ..schemas import token as token_schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=user_schemas.User)
async def signup(user_in: user_schemas.UserCreate, db: AsyncSession = Depends(get_db_async)):
    # Check if user exists
    result = await db.execute(select(models.User).filter((models.User.email == user_in.email) | (models.User.username == user_in.username)))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists.",
        )
    
    # Create new user
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=token_schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db_async)
):
    # Authenticate user
    # Note: OAuth2PasswordRequestForm puts the email/username in the 'username' field
    result = await db.execute(select(models.User).filter((models.User.username == form_data.username) | (models.User.email == form_data.username)))
    user = result.scalars().first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
