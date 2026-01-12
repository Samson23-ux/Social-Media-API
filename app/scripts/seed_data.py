from app.dependencies import get_db
from app.core.config import settings
from app.core.exceptions import ServerError
from app.api.v1.services.auth_service import user_service_v1
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.schemas.users import UserCreateV1, RoleCreateV1



# seed dB with roles
def create_roles():
    admin_role = RoleCreateV1(name='admin')
    user_role = RoleCreateV1(name='user')

    db_gen = get_db()
    db = next(db_gen)
    user_service_v1.create_role(admin_role, db)
    user_service_v1.create_role(user_role, db)

# create a first and core admin user
def create_admin_user():
    user_create = UserCreateV1(
        display_name=settings.ADMIN_DISPLAY_NAME,
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        hash_password=settings.ADMIN_PASSWORD,
        dob=settings.ADMIN_DOB,
        nationality=settings.ADMIN_NATIONALITY,
        bio=settings.ADMIN_BIO
    )

    db_gen = get_db()
    db = next(db_gen)
    try:
        auth_service_v1.sign_up(user_create, db)
    finally:
        db.close()


if __name__ == '__main__':
    create_roles()
    create_admin_user()
