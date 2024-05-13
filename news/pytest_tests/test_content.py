import pytest

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, bunch_news, home_url):
    assert (client.get(home_url)
            .context['object_list']
            .count() == settings.NEWS_COUNT_ON_HOME_PAGE)


def test_news_order(client, bunch_news, home_url):
    all_dates = [
        news.date for news in client.get(home_url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, one_news, many_comments, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    count_comments = all_comments.count()
    assert count_comments == settings.NEWS_COUNT_ON_HOME_PAGE
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, one_news, detail_url):
    assert 'form' not in client.get(detail_url).context


def test_authorized_client_has_form(author_client, one_news, detail_url):
    assert 'form' in author_client.get(detail_url).context
    assert isinstance(
        author_client.get(detail_url).context['form'], CommentForm
    )
