from app.dependencies import get_db
from app.schedules.celery_app import app
from app.core.exceptions import ServerError
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.services.auth_service import auth_service_v1


#Background task to delete user accounts permanently
#Deletion happens after 30 days of disabling account
@app.task
def delete_accounts():
    db_gen = get_db()
    db = next(db_gen)
    user_service_v1.delete_user_accounts(db)


#Clean up used or revoked refresh tokens from db
@app.task
def delete_refresh_tokens():
    db_gen = get_db()
    db = next(db_gen)
    auth_service_v1.delete_refresh_tokens(db)

