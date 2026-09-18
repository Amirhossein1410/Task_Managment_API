from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.config import DATABASE_URL
from sqlalchemy.orm import sessionmaker , DeclarativeBase

engine = create_engine(DATABASE_URL)

SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine, autoflush=False, autocommit=False)
class Base(DeclarativeBase):
    __abstract__ = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[
    Session,
    Depends(get_db)
]

