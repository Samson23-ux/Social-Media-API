from sqlalchemy.orm import sessionmaker, Session

from app.database.session import db_engine
from app.core.config import settings
from app.api.v1.services.auth_service import user_service_v1
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.schemas.users import UserCreateV1, RoleCreateV1


SessionLocal: Session = sessionmaker(
    autoflush=False, autocommit=False, bind=db_engine, expire_on_commit=False
)


# seed dB with roles
def create_roles():
    admin_role = RoleCreateV1(name='admin')
    user_role = RoleCreateV1(name='user')

    with SessionLocal() as db:
        user_service_v1.create_role(admin_role, db)
        user_service_v1.create_role(user_role, db)


# create a first and core admin user
def create_admin_user():
    user_create = UserCreateV1(
        display_name=settings.ADMIN_DISPLAY_NAME,
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        password=settings.ADMIN_PASSWORD,
        dob=settings.ADMIN_DOB,
        nationality=settings.ADMIN_NATIONALITY,
        bio=settings.ADMIN_BIO,
    )

    with SessionLocal() as db:
        auth_service_v1.sign_up(user_create, db, admin=True)


if __name__ == '__main__':
    create_roles()
    create_admin_user()
