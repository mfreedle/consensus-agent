import logging
import os

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
    """Create database tables and seed initial data"""
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
        
        # Seed initial data
        await seed_initial_data()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def seed_initial_data():
    """Seed the database with default models and admin user"""
    try:
        logger.info("Starting to seed initial data...")
        await seed_models()
        await create_default_user()
        logger.info("Initial data seeding completed successfully")
    except Exception as e:
        logger.error(f"Failed to seed initial data: {e}")
        raise

async def seed_models():
    """Seed the database with default LLM models"""
    from app.models.llm_model import LLMModel
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        # Check if models already exist
        result = await session.execute(select(LLMModel))
        existing_models = result.scalars().all()
        
        if existing_models:
            logger.info("Models already seeded.")
            return
        
        # Default models
        models = [
            LLMModel(
                provider="openai",
                model_id="gpt-4o",
                display_name="GPT-4o",
                description="Most capable OpenAI model for complex tasks",
                max_tokens=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={"vision": True, "reasoning": True, "code": True}
            ),
            LLMModel(
                provider="openai",
                model_id="gpt-4o-mini",
                display_name="GPT-4o Mini",
                description="Fast and efficient model for simpler tasks",
                max_tokens=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={"vision": True, "reasoning": True, "code": True}
            ),
            LLMModel(
                provider="grok",
                model_id="grok-beta",
                display_name="Grok Beta",
                description="xAI's powerful language model",
                max_tokens=131072,
                supports_streaming=True,
                supports_function_calling=False,
                supports_vision=False,
                capabilities={"reasoning": True, "real_time": True}
            ),
            LLMModel(
                provider="deepseek",
                model_id="deepseek-chat",
                display_name="DeepSeek Chat",
                description="Efficient model for coding and reasoning",
                max_tokens=64000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={"code": True, "reasoning": True}
            ),
        ]
        
        for model in models:
            session.add(model)
        
        await session.commit()
        logger.info(f"Seeded {len(models)} LLM models")

async def create_default_user():
    """Create a default admin user"""
    from app.auth.utils import get_password_hash
    from app.models.user import User
    from sqlalchemy import select

    # Get default admin credentials from environment or use defaults
    admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "password123")
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if default user exists
            result = await session.execute(select(User).where(User.username == admin_username))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info(f"Default admin user '{admin_username}' already exists.")
                return
            
            # Create default user
            hashed_password = get_password_hash(admin_password)
            user = User(
                username=admin_username,
                password_hash=hashed_password,
                is_active=True
            )
            
            session.add(user)
            await session.commit()
            logger.info(f"Created default admin user: {admin_username} with password: {admin_password}")
            
    except Exception as e:
        logger.error(f"Failed to create default admin user: {e}")
        raise
