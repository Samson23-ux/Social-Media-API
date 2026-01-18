from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.schedules.celery_app import app
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.services.user_service import user_service_v1


db_engine: Engine = create_engine(
    url=settings.WORKER_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        'options': '-c timezone=utc'
    }
)

SessionLocal: Session = sessionmaker(autoflush=False, autocommit=False, bind=db_engine)

# background task to delete revoked or used refresh tokens
@app.task
def delete_refresh_tokens():
    with SessionLocal() as db:
        auth_service_v1.delete_refresh_tokens(db)

# background task to delete users permanently
@app.task
def delete_users():
    with SessionLocal() as db:
        user_service_v1.delete_user_accounts(db)
