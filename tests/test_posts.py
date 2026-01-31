from uuid import uuid4
from pathlib import Path


from app.core.config import settings
from tests.fake_data import user_create_1, user_create_2, post_create_1


def test_get_feed_posts(create_role, create_post, test_client):
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    res = test_client.get(
        '/api/v1/posts/feed/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert len(res.json()['data']) >= 1


def test_get_following_posts(create_role, create_post, test_client):
    test_client.post('/api/v1/auth/sign-up/', json=user_create_2)

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_2.get('email'),
            'password': user_create_2.get('password'),
        },
    )

    test_client.patch(
        f'/api/v1/users/{user_create_1.get('username')}/follow/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    res = test_client.get(
        '/api/v1/posts/following/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert len(res.json()['data']) >= 1


def test_get_search_posts(create_role, create_post, test_client):
    test_client.post('/api/v1/auth/sign-up/', json=user_create_2)

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_2.get('email'),
            'password': user_create_2.get('password'),
        },
    )

    res = test_client.get(
        f'/api/v1/posts/search/?q={post_create_1.get('title')}',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert len(res.json()['data']) >= 1


def test_get_post_by_id(create_role, create_post, test_client):
    post = create_post
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    res = test_client.get(
        f'/api/v1/posts/{post_id}/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_get_post_not_found(create_role, create_post, test_client):
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    res = test_client.get(
        f'/api/v1/posts/{uuid4()}/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 404


def test_get_posts_comments(create_role, create_post, test_client):
    post = create_post
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    test_client.post(
        f'/api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    res = test_client.get(
        f'/api/v1/posts/{post_id}/comments/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert len(res.json()['data']) >= 1


def test_get_comment(create_role, create_post, test_client):
    post = create_post
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    comment_res = test_client.post(
        f'/api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    comment_id = comment_res.json()['data']['id']

    res = test_client.get(
        f'/api/v1/posts/{post_id}/comments/{comment_id}/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_comment_not_found(create_role, create_post, test_client):
    post = create_post
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    res = test_client.get(
        f'/api/v1/posts/{post_id}/comments/{uuid4()}/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 404


def test_create_post(create_role, create_post, test_client):
    assert create_post.status_code == 201
    assert 'id' in create_post.json()['data']


def test_unauthenticated_posts(test_client):
    res = test_client.post('/api/v1/posts/', json=post_create_1)

    assert res.status_code == 401


def test_create_comment(create_role, create_post, test_client):
    post = create_post
    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    res = test_client.post(
        f'/api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 201


def test_update_post(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    res = test_client.patch(
        f'/api/v1/posts/{post_id}/',
        json={'content': 'fake_update'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.json()['data']['content'] == 'fake_update'


def test_like_post(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    res = test_client.patch(
        f'/api/v1/posts/{post_id}/like/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_unlike_post(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    test_client.patch(
        f'/api/v1/posts/{post_id}/like/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    res = test_client.patch(
        f'/api/v1/posts/{post_id}/unlike/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_like_comment(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    comment_res = test_client.post(
        f'/api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    comment_id = comment_res.json()['data']['id']

    res = test_client.patch(
        f'/api/v1/posts/{post_id}/comments/{comment_id}/like/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_unlike_comment(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    comment_res = test_client.post(
        f'/api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    comment_id = comment_res.json()['data']['id']

    test_client.patch(
        f'/api/v1/posts/{post_id}/comments/{comment_id}/like/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    res = test_client.patch(
        f'/api/v1/posts/{post_id}/comments/{comment_id}/unlike/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200


def test_delete_post(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    res = test_client.delete(
        f'/api/v1/posts/{post_id}/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 204


def test_delete_comment(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']

    comment_res = test_client.post(
        f'/api/v1/posts/{post_id}/comments/',
        json={'content': 'fake_comment'},
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    comment_id = comment_res.json()['data']['id']

    res = test_client.delete(
        f'/api/v1/posts/{post_id}/comments/{comment_id}/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 204


def test_get_post_image(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']
    source_path = Path(__file__).parent / 'assets' / '20240811_012037.jpg'

    with open(source_path, 'rb') as f:
        test_client.post(
            f'/api/v1/posts/{post_id}/images/',
            headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
            files={'post_images': ('20240811_012037.jpg', f, 'image/jpg')},
        )

    res = test_client.get(
        f'/api/v1/posts/{post_id}/images/20240811_012037.jpg/',
        headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
    )

    assert res.status_code == 200
    assert res.headers['content-type'].startswith('image')

    image_path: Path = Path(settings.POST_IMAGE_PATH) / '20240811_012037.jpg'

    assert image_path.exists()
    image_path.unlink()


def test_create_post_image(create_role, create_post, test_client):
    post = create_post

    sign_in_res = test_client.post(
        '/api/v1/auth/sign-in/',
        data={
            'username': user_create_1.get('email'),
            'password': user_create_1.get('password'),
        },
    )

    post_id = post.json()['data']['id']
    source_path = Path(__file__).parent / 'assets' / '20240811_012037.jpg'

    with open(source_path, 'rb') as f:
        res = test_client.post(
            f'/api/v1/posts/{post_id}/images/',
            headers={'Authorization': f'Bearer {sign_in_res.json()['access_token']}'},
            files={'post_images': ('20240811_012037.jpg', f, 'image/jpg')},
        )

    assert res.status_code == 201
    assert '20240811_012037.jpg' in res.json()['data']['image_url']

    image_path: Path = Path(settings.POST_IMAGE_PATH) / '20240811_012037.jpg'

    assert image_path.exists()
    image_path.unlink()
