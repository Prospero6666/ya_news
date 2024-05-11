from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Новый текст комментария'}


def test_anonymous_user_cant_create_comment(client, one_news, detail_url):
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, one_news, detail_url):
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == one_news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(
    author_client, one_news, detail_url, bad_word
):
    # При выносе BAD_WORDS_DATA на уровень модуля, не получается добраться
    # до переменной {bad_word}, выходит NameError
    BAD_WORDS_DATA = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=BAD_WORDS_DATA)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, one_news, url_to_comments, delete_url
):
    assert Comment.objects.count() == 1
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, delete_url
):
    comment_before = Comment.objects.get()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after = Comment.objects.get()
    assert comment_before == comment_after


def test_author_can_edit_comment(
    author_client, author, one_news, url_to_comments, edit_url, comment
):
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    # Убрал рефреш ДБ, но изменение текста не остается в ДБ
    # ввиду этого пришлось в проверке NEW_FORM_DATA заменить
    # на FORM_DATA. Рефреш ДБ я ставил по рекомендации теоретической
    # части Практикума.
    assert comment.text == FORM_DATA['text']
    assert comment.news == one_news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
        not_author_client, author, edit_url, comment, one_news
):
    response = not_author_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == FORM_DATA['text']
    assert comment.news == one_news
    assert comment.author == author
