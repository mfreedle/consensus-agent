import logging
from datetime import timedelta

from app.auth.dependencies import get_current_active_user
from app.auth.utils import (create_access_token, get_password_hash,
                            verify_password)
from app.config import settings
from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import (PasswordChange, Token, UserCreate, UserLogin,
                              UserResponse, UserUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    # Check if username already exists
    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists (if provided)
    if user_data.email:
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access token"""
    
    logger = logging.getLogger(__name__)
    logger.info(f"Login attempt for username: {user_credentials.username}")
    
    # Get user from database
    stmt = select(User).where(User.username == user_credentials.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"User not found: {user_credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User found: {user.username}, checking password...")
    
    # Verify password
    password_valid = verify_password(user_credentials.password, user.password_hash)
    logger.info(f"Password verification result: {password_valid}")
    
    if not password_valid:
        logger.warning(f"Invalid password for user: {user_credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}

@router.put("/change-password")
async def change_password(
    password_data: PasswordChange, 
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, str(current_user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password using SQLAlchemy update
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(password_hash=get_password_hash(password_data.new_password))
    )
    await db.commit()
    
    return {"message": "Password updated successfully"}

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    
    # Check if email already exists (if provided and different from current)
    if user_data.email and str(user_data.email) != str(current_user.email):
        stmt = select(User).where(User.email == str(user_data.email))
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Update user email
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(email=str(user_data.email))
        )
        await db.commit()
        
        # Return updated user
        stmt = select(User).where(User.id == current_user.id)
        result = await db.execute(stmt)
        return result.scalar_one()
    
    return current_user
    return current_user
