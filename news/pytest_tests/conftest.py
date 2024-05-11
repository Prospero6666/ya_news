from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(one_news):
    return reverse('news:detail', args=(one_news.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def url_to_comments(detail_url):
    return detail_url + '#comments'


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def login():
    return reverse('users:login')


@pytest.fixture
def logout():
    return reverse('users:logout')


@pytest.fixture
def signup():
    return reverse('users:signup')


@pytest.fixture
def redirect(login):
    def redirect_next(next_url):
        return f'{login}?next={next_url}'
    return redirect_next


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def bunch_news():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def one_news():
    return News.objects.create(
        title='Новость',
        text='Просто текст.',
    )


@pytest.fixture
def comment(one_news, author):
    return Comment.objects.create(
        news=one_news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def many_comments(one_news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=one_news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
