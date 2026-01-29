from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL: str = 'sqlite:///./test.db'

db_engine: Engine = create_engine(url=DATABASE_URL, connect_args={'check_same_thread': False})

TestSessionLocal: Session = sessionmaker(autoflush=False, autocommit=False, bind=db_engine)


def test_get_db():
    with TestSessionLocal() as db:
        yield db
