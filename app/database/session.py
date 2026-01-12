from app import models
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

db_engine: Engine = create_engine(
    url=settings.DATABASE_URL,
    connect_args={
        'options': '-c timezone=utc'
    },  # set session timezone to utc on connection with db
)

SessionLocal: Session = sessionmaker(autoflush=False, autocommit=False, bind=db_engine)
