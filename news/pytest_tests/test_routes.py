from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db

CLIENT = pytest.lazy_fixture('client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')

HOME = pytest.lazy_fixture('home_url')
DETAIL = pytest.lazy_fixture('detail_url')
LOGIN = pytest.lazy_fixture('login')
LOGOUT = pytest.lazy_fixture('logout')
SIGNUP = pytest.lazy_fixture('signup')
EDIT = pytest.lazy_fixture('edit_url')
DELETE = pytest.lazy_fixture('delete_url')
REDIRECT_EDIT = pytest.lazy_fixture('redirect_edit_url')
REDIRECT_DELETE = pytest.lazy_fixture('redirect_delete_url')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME, CLIENT, HTTPStatus.OK),
        (DETAIL, CLIENT, HTTPStatus.OK),
        (LOGIN, CLIENT, HTTPStatus.OK),
        (LOGOUT, CLIENT, HTTPStatus.OK),
        (SIGNUP, CLIENT, HTTPStatus.OK),
        (EDIT, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE, AUTHOR_CLIENT, HTTPStatus.OK),
    ),
)
def test_status_codes_for_anonyms_and_users(
    url, parametrized_client, expected_status
):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, parametrized_client, redirect_url',
    (
        (EDIT, CLIENT, REDIRECT_EDIT),
        (DELETE, CLIENT, REDIRECT_DELETE)
    ),
)
def test_redirect_for_anonymous_client(url, parametrized_client, redirect_url):
    response = parametrized_client.get(url)
    assertRedirects(response, redirect_url)
