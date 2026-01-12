from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.schedules.celery_app import app
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.services.auth_service import auth_service_v1



db_engine: Engine = create_engine(
    url=settings.DATABASE_URL,
    connect_args={
        'options': '-c timezone=utc'
    },  # set session timezone to utc on connection with db
)

SessionLocal: Session = sessionmaker(autoflush=False, autocommit=False, bind=db_engine)


#Background task to delete user accounts permanently
#Deletion happens after 30 days of disabling account
@app.task
def delete_accounts():
    db: Session = SessionLocal()
    try:
        user_service_v1.delete_user_accounts(db)
    finally:
        db.close()


#Clean up used or revoked refresh tokens from db
@app.task
def delete_refresh_tokens():
    db: Session = SessionLocal()
    try:
        auth_service_v1.delete_refresh_tokens(db)
    finally:
        db.close()
        
