from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from server.config import DATABASE_URL

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Async session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency generator for FastAPI endpoints
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session: # Automatically manages the session lifecycle (open, close)
        yield session
