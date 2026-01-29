import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.base import Base
from app.dependencies import get_db
from tests.config import db_engine, test_get_db

from tests.fake_data import user_create_1, post_create_1
from app.api.v1.services.auth_service import user_service_v1
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.schemas.users import UserCreateV1, RoleCreateV1


@pytest.fixture(scope='function', autouse=True)
def create_test_db():
    print('Table created')
    Base.metadata.create_all(bind=db_engine)
    yield
    Base.metadata.drop_all(bind=db_engine)


app.dependency_overrides[get_db] = test_get_db


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def create_role():
    admin_role = RoleCreateV1(name='admin')
    user_role = RoleCreateV1(name='user')

    db_gen = test_get_db()
    db = next(db_gen)
    user_service_v1.create_role(admin_role, db)
    user_service_v1.create_role(user_role, db)


@pytest.fixture
def create_admin(create_role):
    user_create = UserCreateV1(
        display_name='fake_admin',
        username='@fake_admin',
        email='admin_user@example.com',
        password='fakepassword',
        dob='1999-05-20',
        nationality='fake_nationality',
        bio='admin...'
    )

    db_gen = test_get_db()
    db = next(db_gen)
    auth_service_v1.sign_up(user_create, db)


@pytest.fixture
def sign_up(test_client):
    res = test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_1
    )
    return res

@pytest.fixture
def create_post(sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.post(
        'api/v1/posts/',
        json=post_create_1,
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )
    return res
