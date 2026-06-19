import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)

Base = declarative_base()

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
