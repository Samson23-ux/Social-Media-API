from tests.fake_data import user_create_1

'''tests are independent and can run alone and pass'''

def test_get_suspended_users(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    test_client.patch(
        f'api/v1/admin/users/{user_create_1.get('username')}/suspend/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    res = test_client.get(
        'api/v1/admin/users/suspended/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )
    assert res.status_code == 200
    assert res.json()['data']


def test_unauthenticated_admin(create_admin, test_client):
    res = test_client.get('api/v1/admin/users/suspended/')

    assert res.status_code == 401


def test_unauthorized_admin(create_admin, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        'api/v1/admin/users/suspended/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 403


def test_no_suspended_users(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    res = test_client.get(
        'api/v1/admin/users/suspended/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )
    assert res.status_code == 404


def test_get_active_users(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    res = test_client.get(
        'api/v1/admin/users/all/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 200
    assert res.json()['data']


def test_assign_admin(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    res = test_client.patch(
        f'api/v1/admin/users/{user_create_1.get('username')}/assign-admin-role/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 200


def test_user_not_found(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    res = test_client.get(
        'api/v1/admin/users/@fake_user/assign-admin-role/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 404


def test_suspend_user(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    res = test_client.patch(
        f'api/v1/admin/users/{user_create_1.get('username')}/suspend/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 200

def test_unsuspend_user(create_admin, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': '@fake_admin', 'password': 'fakepassword'}
    )

    test_client.patch(
        f'api/v1/admin/users/{user_create_1.get('username')}/suspend/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    res = test_client.patch(
        f'api/v1/admin/users/{user_create_1.get('username')}/unsuspend/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 200
