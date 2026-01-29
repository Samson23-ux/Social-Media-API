import os
from pathlib import Path

from app.core.config import settings
from tests.fake_data import user_create_1, user_create_2, user_create_3

'''tests are independent and can run alone and pass'''

def test_get_users(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_2
    )

    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_3
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        'api/v1/users/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert len(res.json()['data']) > 1


def test_filter_users(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_2
    )

    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_3
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        f'api/v1/users/?nationality={user_create_3.get('nationality')}',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.json()['data']['username'] == user_create_3.get('username')


def test_search_users(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_3
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        f'api/v1/users/?q={user_create_3.get('username')}',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.json()['data']['username'] == user_create_3.get('username')


def test_users_not_found(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        f'api/v1/users/?q={user_create_3.get('username')}',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 404


def test_get_user(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_3
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        f'api/v1/users/{user_create_3.get('username')}/profile/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.json()['data']['username'] == user_create_3.get('username')


def test_user_not_found(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        'api/v1/users/not_found_user/profile/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 404


def test_get_profile(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        'api/v1/users/me/profile/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.json()['data']['username'] == user_create_1.get('username')


def test_unauthenticated_users(sign_up, test_client):
    res = test_client.get('api/v1/users/me/profile/')

    assert res.status_code == 401


def test_update_user(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.patch(
        'api/v1/update/me/',
        json={'nationality': 'American'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.json()['data']['nationality'] == 'American'


def test_get_followers(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_2
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    test_client.patch(
        f'api/v1/users/{user_create_2.get('username')}/follow/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    res = test_client.get(
        f'api/v1/{user_create_2.get('username')}/followers/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_get_followings(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_2
    )

    sign_in_res1 = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    sign_in_res2 = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_2.get('email'), 'password': user_create_2.get('password')}
    )

    test_client.patch(
        f'api/v1/users/{user_create_2.get('username')}/follow/',
        headers={'Authorization': f'Bearer {sign_in_res1.json()['access_token']}'},
    )

    res = test_client.get(
        f'api/v1/{user_create_2.get('username')}/followings/',
        headers={'Authorization': f'Bearer {sign_in_res2.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_follow_user(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_2
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.patch(
        f'api/v1/users/{user_create_2.get('username')}/follow/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_unfollow_user(create_role, sign_up, test_client):
    test_client.post(
        'api/v1/auth/sign-up/',
        json=user_create_2
    )

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    test_client.patch(
        f'api/v1/users/{user_create_2.get('username')}/follow/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    res = test_client.patch(
        f'api/v1/users/{user_create_2.get('username')}/unfollow/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


#### create image
def test_upload_image(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    source_path = Path(__file__).parent/'assets'/'20240811_012037.jpg'

    with open(source_path, 'rb') as f:
        res = test_client.post(
            'api/v1/users/profile/images/upload/',
            headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
            files={'images': [('20240811_012037.jpg', f, 'image/jpg')]}
        )

    assert res.status_code == 201
    assert '20240811_012037.jpg' in res.json()['data']['image_url']

    path: Path = Path(settings.PROFILE_IMAGE_PATH).resolve()
    image_path: str = f'{str(path)}\\20240811_012037.jpg'

    assert os.path.exists(image_path)
    os.remove(image_path)


#### create image
def test_get_user_avatar(create_role, sign_up, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    source_path = Path(__file__).parent/'assets'/'20240811_012037.jpg'

    with open(source_path, 'rb') as f:
        test_client.post(
            'api/v1/users/profile/images/upload/',
            headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
            files={'images': [('20240811_012037.jpg', f, 'image/jpg')]}
        )

    res = test_client.get(
        f'api/v1/users/{user_create_1.get('username')}/profile/images/20240811_012037.jpg/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.headers['content_type'].startswith('/image')

    path: Path = Path(settings.PROFILE_IMAGE_PATH).resolve()
    image_path: str = f'{str(path)}\\20240811_012037.jpg'

    assert os.path.exists(image_path)
    os.remove(image_path)


#### create post
def test_get_user_posts(create_role, sign_up, create_post, test_client):
    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    res = test_client.get(
        f'api/v1/users/{user_create_2.get('username')}/posts/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


### create post then comment on post
def test_get_user_comments(create_role, sign_up, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_1.get('email'), 'password': user_create_1.get('password')}
    )

    post_id = post.json()['data']['id']

    test_client.post(
        f'api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    res = test_client.get(
        f'api/v1/users/{user_create_2.get('username')}/posts/comments/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 200


### create post then like post
def test_get_liked_posts(create_role, sign_up, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        'api/v1/auth/sign-in/',
        data={'username': user_create_2.get('email'), 'password': user_create_2.get('password')}
    )

    post_id = post.json()['data']['id']

    test_client.patch(
        f'api/v1/posts/{post_id}/like/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    res = test_client.get(
        f'api/v1/users/{user_create_2.get('username')}/posts/likes/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'}
    )

    assert res.status_code == 200
    assert len(res.json()['data']) >= 1
