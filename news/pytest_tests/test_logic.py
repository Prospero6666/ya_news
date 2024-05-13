from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Новый текст комментария'}
BAD_WORDS_DATA = {'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'}


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


def test_user_cant_use_bad_words(
    author_client, one_news, detail_url
):
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
    comments_before = Comment.objects.get()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_after = Comment.objects.get()
    assert comments_before.text == comments_after.text
    assert comments_before.news == comments_after.news
    assert comments_before.author == comments_after.author


def test_author_can_edit_comment(
    author_client, url_to_comments, edit_url, comment
):
    original_comment = Comment.objects.get(id=comment.pk)
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    edited_comment = Comment.objects.get(id=comment.pk)
    assert edited_comment.text == NEW_FORM_DATA['text']
    assert edited_comment.news == original_comment.news
    assert edited_comment.author == original_comment.author


def test_user_cant_edit_comment_of_another_user(
        not_author_client, edit_url, comment
):
    original_comment = Comment.objects.get(id=comment.pk)
    response = not_author_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    edited_comment = Comment.objects.get(id=comment.pk)
    assert edited_comment.text == original_comment.text
    assert edited_comment.news == original_comment.news
    assert edited_comment.author == original_comment.author
