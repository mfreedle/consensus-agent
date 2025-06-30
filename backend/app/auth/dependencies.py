from app.auth.utils import verify_token
from app.database.connection import get_db
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    
    # Verify token
    try:
        token_data = verify_token(credentials.credentials)
        username = token_data.get("username")  # This should match what verify_token returns
        
        if username is None:
            print("[AUTH DEBUG] Token verification failed: username is None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"[AUTH DEBUG] Token verified for username: {username}")
        
        # Get user from database
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            print(f"[AUTH DEBUG] User not found in database: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            print(f"[AUTH DEBUG] User is inactive: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        print(f"[AUTH DEBUG] User authenticated successfully: {username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH DEBUG] Unexpected error during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_from_token(token: str) -> User:
    """Get current user from JWT token string (for Socket.IO)"""
    from app.auth.utils import verify_token
    from app.database.connection import get_db
    from app.models.user import User
    from fastapi import HTTPException, status
    from sqlalchemy import select
    
    token_data = verify_token(token)
    username = token_data.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db = await get_db().__anext__()
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user
