from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from Setting.Config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)

Base = declarative_base()

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session
