from tests.fake_data import user_create_1

'''tests are independent and can run alone and pass'''

def test_sign_up(create_role, sign_up):
    res = sign_up
    assert res.status_code == 201
    assert 'id' in res.json()['data']


def test_duplicate_user(create_role, sign_up, test_client):
    '''create an existing user'''
    res = test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_1
    )
    assert res.status_code == 400


def test_sign_in(create_role, sign_up, test_client):
    res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )
    assert res.status_code == 201
    assert 'access_token' in res.json()

def test_incorrect_creds(create_role, sign_up, test_client):
    res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': 'password'}
    )
    assert res.status_code == 400

def test_get_access_token(create_role, sign_up, test_client):
    '''request for a new access token with a valid refresh token'''
    test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get('/auth/refresh/')
    assert res.status_code == 200
    assert 'access_token' in res.json()['data']

def test_sign_out(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.patch(
        'api/v1/auth/sign-out/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )
    assert res.status_code == 200

def test_update_password(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )
    res = test_client.patch(
        'api/v1/auth/update-password/',
        data={'curr_password': user_create_1.get('password'), 'new_password': 'random_password123'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    res_to_json = res.json()['data']
    assert res_to_json['username'] == user_create_1.get('username')


def test_reset_password(create_role, sign_up, test_client):
    res = test_client.patch(
        'api/v1/auth/reset-password/',
        data={'email': user_create_1.get('email'), 'new_password': 'new_rand_int'}
    )

    assert res.status_code == 200


def test_user_not_found(create_role, sign_up, test_client):
    '''test incorrect email for password reset'''
    res = test_client.patch(
        'api/v1/auth/reset-password/',
        data={'email': 'email.example.com', 'new_password': 'new_rand_int'}
    )

    assert res.status_code == 404

def test_reactivate_account(create_role, sign_up, test_client):
    res = test_client.patch(
        'api/v1/auth/account/reactivate/',
        data={'email': user_create_1.get('email'), 'account_password': 'random_password123'},
    )

    assert res.status_code == 200

def test_deactivate_account(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.patch(
        'api/v1/auth/account/deactivate/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_delete_account(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.request(
        'DELETE',
        'api/v1/auth/account/delete/',
        data={'password': user_create_1.get('password')},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 204

def test_unauthenticated_auth(create_role, sign_up, test_client):
    res = test_client.request(
        'DELETE',
        'api/v1/auth/account/delete/',
        data={'password': user_create_1.get('password')},
    )

    assert res.status_code == 401
