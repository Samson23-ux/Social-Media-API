from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.models.users import User, Role
from app.database.session import db_engine
from app.core.security import hash_password
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.schemas.users import UserCreateV1, RoleCreateV1, UserInDBV1


SessionLocal: Session = sessionmaker(
    autoflush=False, autocommit=False, bind=db_engine, expire_on_commit=False
)


# seed dB with roles
def create_roles():
    admin_role = RoleCreateV1(name='admin')
    user_role = RoleCreateV1(name='user')

    with SessionLocal() as db:
        admin_role_db: Role | None = user_repo_v1.get_role(admin_role.name, db)

        if not admin_role_db:
            role_db: Role = Role(name=admin_role.name)
            user_repo_v1.create_role(role_db, db)

        user_role_db: Role | None = user_repo_v1.get_role(user_role.name, db)

        if not user_role_db:
            user_db: Role = Role(name=user_role.name)
            user_repo_v1.create_role(user_db, db)

        db.commit()


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
        user_with_email: User | None = user_repo_v1.get_user_by_email(user_create.email, db)
        user_with_username: User | None = user_repo_v1.get_user_by_username(user_create.username, db)

        if not user_with_email and not user_with_username:
            user_create.password = hash_password(user_create.password)
            user_in_db: UserInDBV1 = UserInDBV1(**user_create.model_dump())

            role: Role = user_repo_v1.get_role('admin', db)

            user: User = User(
                **user_in_db.model_dump(exclude={'role', 'password'}),
                role_id=role.id,
                hash_password=user_create.password
            )

            user_repo_v1.add_user(user, db)

        db.commit()


if __name__ == '__main__':
    create_roles()
    create_admin_user()
