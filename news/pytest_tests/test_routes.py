from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('home_url'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('detail_url'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('login'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('logout'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('signup'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
def test_status_codes_for_anonyms_and_users(
    url, parametrized_client, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, parametrized_client',
    (
        (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('client')),
        (pytest.lazy_fixture('delete_url'), pytest.lazy_fixture('client'))
    ),
)
def test_redirect_for_anonymous_client(url, parametrized_client, redirect):
    response = parametrized_client.get(url)
    expected_url = redirect(url)
    assertRedirects(response, expected_url)
