import logging
import os

from app.config import settings
from sqlalchemy import MetaData, text
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
        
        # Run migrations
        await migrate_database()
        
        # Seed initial data
        await seed_initial_data()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def seed_initial_data():
    """Seed the database with default models and admin user"""
    import os
    
    try:
        logger.info("Starting to seed initial data...")
        
        # Check if we're on Railway (production) and force refresh models
        is_railway = bool(os.environ.get('RAILWAY_ENVIRONMENT_NAME'))
        if is_railway:
            logger.info("Railway deployment detected - forcing model refresh to ensure all models are available")
            await seed_models(force_refresh=True)
        else:
            await seed_models()
            
        await create_default_user()
        logger.info("Initial data seeding completed successfully")
    except Exception as e:
        logger.error(f"Failed to seed initial data: {e}")
        raise

async def seed_models(force_refresh=False):
    """Seed the database with comprehensive LLM models
    
    Args:
        force_refresh: If True, clears existing models and reseeds
    """
    from app.models.llm_model import LLMModel
    from sqlalchemy import delete, select
    
    async with AsyncSessionLocal() as session:
        # Check if models already exist
        result = await session.execute(select(LLMModel))
        existing_models = result.scalars().all()
        
        if existing_models and not force_refresh:
            logger.info(f"Models already exist ({len(existing_models)} models). Skipping seeding. Use force_refresh=True to reseed.")
            return
        elif existing_models and force_refresh:
            # Clear existing models
            await session.execute(delete(LLMModel))
            logger.info("Cleared existing models for refresh")
        
        # Comprehensive models list from LLM_models_to_use.md
        models = [
            # Grok Models
            LLMModel(
                provider="grok",
                model_id="grok-4-latest",
                display_name="Grok 4 Latest",
                description="Latest version of Grok 4 with enhanced reasoning capabilities",
                max_tokens=4096,
                context_window=256000,
                supports_streaming=True,
                supports_function_calling=False,
                supports_vision=False,
                is_active=True,
                capabilities={
                    "reasoning": "exceptional",
                    "mathematics": "high",
                    "science": "high",
                    "coding": "high",
                    "research": "high"
                }
            ),
            LLMModel(
                provider="grok",
                model_id="grok-3-latest",
                display_name="Grok 3 Latest",
                description="Latest Grok 3 model with enhanced capabilities",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=False,
                supports_vision=False,
                is_active=True,
                capabilities={
                    "reasoning": "very_high",
                    "creativity": "high",
                    "humor": "high"
                }
            ),
            LLMModel(
                provider="grok",
                model_id="grok-3-mini-latest",
                display_name="Grok 3 Mini Latest",
                description="Smaller, faster version of Grok 3",
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_function_calling=False,
                supports_vision=False,
                capabilities={
                    "reasoning": "high",
                    "speed": "very_high",
                    "efficiency": "very_high"
                }
            ),
            LLMModel(
                provider="grok",
                model_id="grok-3-fast-latest",
                display_name="Grok 3 Fast Latest",
                description="Optimized for speed version of Grok 3",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=False,
                supports_vision=False,
                capabilities={
                    "reasoning": "high",
                    "speed": "exceptional",
                    "efficiency": "high"
                }
            ),
            LLMModel(
                provider="grok",
                model_id="grok-3-mini-fast-latest",
                display_name="Grok 3 Mini Fast Latest",
                description="Fastest and most efficient Grok variant",
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_function_calling=False,
                supports_vision=False,
                capabilities={
                    "reasoning": "medium",
                    "speed": "exceptional",
                    "efficiency": "exceptional"
                }
            ),
            LLMModel(
                provider="grok",
                model_id="grok-2-image-latest",
                display_name="Grok 2 Image Latest",
                description="Latest xAI image generation model",
                max_tokens=1024,
                context_window=32000,
                supports_streaming=False,
                supports_function_calling=False,
                supports_vision=False,
                capabilities={
                    "image_generation": True,
                    "creativity": "high",
                    "artistic": "high"
                }
            ),
            
            # OpenAI GPT Models
            LLMModel(
                provider="openai",
                model_id="gpt-4.1",
                display_name="GPT-4.1",
                description="Latest GPT-4 series model with enhanced capabilities",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={
                    "reasoning": "very_high",
                    "creativity": "high",
                    "coding": "high",
                    "vision": "high",
                    "function_calling": "high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="gpt-4.1-mini",
                display_name="GPT-4.1 Mini",
                description="Smaller, more efficient version of GPT-4.1",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={
                    "reasoning": "high",
                    "efficiency": "very_high",
                    "speed": "very_high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="gpt-4.1-nano",
                display_name="GPT-4.1 Nano",
                description="Ultra-fast, lightweight version of GPT-4.1",
                max_tokens=2048,
                context_window=32000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "medium",
                    "speed": "exceptional",
                    "efficiency": "exceptional"
                }
            ),
            
            # OpenAI DALL-E
            LLMModel(
                provider="openai",
                model_id="dall-e-3",
                display_name="DALL-E 3",
                description="Advanced image generation model from OpenAI",
                max_tokens=1024,
                context_window=4000,
                supports_streaming=False,
                supports_function_calling=False,
                supports_vision=False,
                capabilities={
                    "image_generation": True,
                    "creativity": "very_high",
                    "artistic": "very_high"
                }
            ),
            
            # OpenAI O-Series Models
            LLMModel(
                provider="openai",
                model_id="o4-mini",
                display_name="O4 Mini",
                description="Compact version of the O4 reasoning model",
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "very_high",
                    "mathematics": "high",
                    "logic": "very_high",
                    "efficiency": "high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="o3",
                display_name="O3",
                description="Advanced reasoning model from OpenAI's O-series",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "exceptional",
                    "mathematics": "very_high",
                    "logic": "exceptional",
                    "problem_solving": "exceptional"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="o3-pro",
                display_name="O3 Pro",
                description="Professional version of O3 with enhanced capabilities",
                max_tokens=8192,
                context_window=256000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "exceptional",
                    "mathematics": "exceptional",
                    "logic": "exceptional",
                    "problem_solving": "exceptional",
                    "research": "very_high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="o3-mini",
                display_name="O3 Mini",
                description="Compact version of O3 reasoning model",
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "very_high",
                    "mathematics": "high",
                    "logic": "very_high",
                    "efficiency": "very_high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="o1",
                display_name="O1",
                description="First generation O-series reasoning model",
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "very_high",
                    "mathematics": "high",
                    "logic": "very_high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="o1-pro",
                display_name="O1 Pro",
                description="Professional version of O1 reasoning model",
                max_tokens=8192,
                context_window=256000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "very_high",
                    "mathematics": "very_high",
                    "logic": "very_high",
                    "research": "high"
                }
            ),
            
            # Deep Research Models
            LLMModel(
                provider="openai",
                model_id="o3-deep-research",
                display_name="O3 Deep Research",
                description="O3 optimized for deep research tasks",
                max_tokens=8192,
                context_window=512000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "exceptional",
                    "research": "exceptional",
                    "analysis": "exceptional",
                    "mathematics": "very_high",
                    "scientific_writing": "very_high"
                }
            ),
            LLMModel(
                provider="openai",
                model_id="o4-mini-deep-research",
                display_name="O4 Mini Deep Research",
                description="O4 Mini optimized for research applications",
                max_tokens=4096,
                context_window=256000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "very_high",
                    "research": "very_high",
                    "analysis": "very_high",
                    "efficiency": "high"
                }
            ),
            
            # DeepSeek Models
            LLMModel(
                provider="deepseek",
                model_id="deepseek-chat",
                display_name="DeepSeek Chat",
                description="Efficient model for coding and reasoning",
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "high",
                    "coding": "very_high",
                    "efficiency": "high"
                }
            ),
            LLMModel(
                provider="deepseek",
                model_id="deepseek-reasoner",
                display_name="DeepSeek Reasoner",
                description="Advanced reasoning model from DeepSeek",
                max_tokens=4096,
                context_window=64000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                capabilities={
                    "reasoning": "very_high",
                    "mathematics": "high",
                    "logic": "very_high"
                }
            ),
            
            # Claude Models
            LLMModel(
                provider="claude",
                model_id="claude-opus-4-0",
                display_name="Claude Opus 4.0",
                description="Most powerful Claude model for complex reasoning",
                max_tokens=8192,
                context_window=512000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={
                    "reasoning": "exceptional",
                    "writing": "exceptional",
                    "analysis": "exceptional",
                    "coding": "very_high",
                    "creativity": "very_high"
                }
            ),
            LLMModel(
                provider="claude",
                model_id="claude-sonnet-4-0",
                display_name="Claude Sonnet 4.0",
                description="Balanced Claude model for general use",
                max_tokens=4096,
                context_window=256000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={
                    "reasoning": "very_high",
                    "writing": "very_high",
                    "analysis": "very_high",
                    "coding": "high",
                    "efficiency": "high"
                }
            ),
            LLMModel(
                provider="claude",
                model_id="claude-3-7-sonnet-latest",
                display_name="Claude 3.7 Sonnet Latest",
                description="Latest version of Claude 3.7 Sonnet",
                max_tokens=4096,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                capabilities={
                    "reasoning": "very_high",
                    "writing": "very_high",
                    "analysis": "very_high",
                    "coding": "high"
                }
            ),
        ]
        
        for model in models:
            session.add(model)
        
        await session.commit()
        logger.info(f"Seeded {len(models)} comprehensive LLM models from LLM_models_to_use.md")

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

async def migrate_database():
    """Handle database migrations"""
    try:
        logger.info("Checking for database migrations...")
        
        # Check if email column exists in users table
        async with engine.begin() as conn:
            if settings.database_url.startswith("postgresql"):
                # PostgreSQL migration
                check_table_exists = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'users'
                """
                result = await conn.execute(text(check_table_exists))
                table_exists = result.fetchone() is not None
                
                if not table_exists:
                    logger.info("Users table doesn't exist yet, will be created by create_all")
                    return
                    
                check_email_column = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'email'
                """
                result = await conn.execute(text(check_email_column))
                email_column_exists = result.fetchone() is not None
                
                if not email_column_exists:
                    logger.info("Adding email column to users table...")
                    add_email_column = """
                    ALTER TABLE users 
                    ADD COLUMN email VARCHAR(255) NULL
                    """
                    await conn.execute(text(add_email_column))
                    
                    # Add unique constraint for email column
                    add_email_unique = """
                    ALTER TABLE users 
                    ADD CONSTRAINT users_email_unique UNIQUE (email)
                    """
                    try:
                        await conn.execute(text(add_email_unique))
                    except Exception as e:
                        logger.warning(f"Could not add unique constraint (might already exist): {e}")
                    
                    # Add index for email column
                    add_email_index = "CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"
                    await conn.execute(text(add_email_index))
                    
                    logger.info("Email column added successfully")
                else:
                    logger.info("Email column already exists")
            else:
                # SQLite migration (already handled by create_all)
                logger.info("SQLite database - using create_all for schema")
                
    except Exception as e:
        logger.warning(f"Migration check failed (table might not exist yet): {e}")
