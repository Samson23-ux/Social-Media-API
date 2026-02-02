import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Engine, text, Connection, RootTransaction

from app.main import app
from app.database.base import Base
from app.dependencies import get_db
from app.core.config import settings
from app.models.users import Role, User
from app.core.security import hash_password
from tests.fake_data import user_create_1, post_create_1
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.services.auth_service import user_service_v1
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.schemas.users import UserCreateV1, RoleCreateV1, UserInDBV1


@pytest.fixture(scope='session')
def test_engine():
    '''create an engine per session'''
    engine: Engine = create_engine(url=settings.TEST_DATABASE_URL)

    with engine.connect() as conn:
        # initialise db with required extensions
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS pg_trgm;'))
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

    Base.metadata.create_all(bind=engine)

    return engine


@pytest.fixture
def test_db_session(test_engine):
    '''establish a session bound to a connection with a transaction and on
    session.commit(), it flushes changes and nothing gets committed to db'''
    connection: Connection = test_engine.connect()
    transaction: RootTransaction = connection.begin()

    TestSessionLocal: Session = sessionmaker(
        autoflush=False, autocommit=False, bind=connection, expire_on_commit=False
    )

    session: Session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_client(test_db_session):
    '''test client runs before every test and the get_db gets overriden'''

    def test_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = test_get_db

    with TestClient(app) as client:
        yield client


@pytest.fixture
def create_role(test_db_session):
    admin_role = RoleCreateV1(name='admin')
    user_role = RoleCreateV1(name='user')

    db = test_db_session
    admin_role_db: Role | None = user_repo_v1.get_role(admin_role.name, db)

    if not admin_role_db:
        role_db: Role = Role(name=admin_role.name)
        user_repo_v1.create_role(role_db, db)

    user_role_db: Role | None = user_repo_v1.get_role(user_role.name, db)

    if not admin_role_db:
        user_db: Role = Role(name=user_role.name)
        user_repo_v1.create_role(user_db, db)


@pytest.fixture
def create_admin(test_db_session, create_role):
    user_create = UserCreateV1(
        display_name='fake_admin',
        username='@fake_admin',
        email='admin_user@example.com',
        password='fakepassword',
        dob='1999-05-20',
        nationality='fake_nationality',
        bio='admin...',
    )

    db = test_db_session
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


@pytest.fixture
def sign_up(test_client):
    res = test_client.post('/api/v1/auth/sign-up/', json=user_create_1)
    return res


@pytest.fixture
def create_post(sign_up, test_client):
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    res = test_client.post(
        '/api/v1/posts/',
        json=post_create_1,
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )
    return res
