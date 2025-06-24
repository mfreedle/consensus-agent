import logging

from app.config import settings
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

# Create async engine
if settings.database_url.startswith("postgresql"):
    # Convert postgresql:// to postgresql+asyncpg://
    async_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
elif settings.database_url.startswith("sqlite"):
    # Handle SQLite URL correctly
    if "aiosqlite" not in settings.database_url:
        async_url = settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    else:
        async_url = settings.database_url
else:
    async_url = settings.database_url

engine = create_async_engine(
    async_url,
    echo=settings.app_env == "development",
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create base model
Base = declarative_base()

# Dependency to get database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    """Create database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from app.models.chat import ChatSession, Message
            from app.models.file import File
            from app.models.llm_model import LLMModel
            from app.models.user import User

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
