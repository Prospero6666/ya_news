import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, bunch_news, home_url):
    response = client.get(home_url)
    assert response.context['object_list'].count() == \
           settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, bunch_news, home_url):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, one_news, many_comments, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    count_comments = all_comments.count()
    assert count_comments == 10
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, one_news, detail_url):
    assert 'form' not in client.get(detail_url).context


def test_authorized_client_has_form(author_client, one_news, detail_url):
    response = author_client.get(detail_url)
    # Если все сделать в Assert, то ошибка длины кода получается
    assert 'form' in response.context and \
           isinstance(response.context['form'], CommentForm)
