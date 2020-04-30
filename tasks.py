from datetime import time

import requests
from celery import Celery, Task
from celery.schedules import crontab
from dateutil.parser import parse
from kombu import Queue, Exchange
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from algoliasearch.search_client import SearchClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.db.session import db_session
from app import settings
from app.models.channel import Channel
from app.models.video import Video

app = Celery('tasks')
app.conf.broker_url = 'redis://redis:6379/0'
app.conf.broker_transport_options = {'visibility_timeout': 3600}
app.conf.beat_schedule = {
    'add-new-videos-from-channels-every-day-in-midnight': {
        'task': 'tasks.get_videos_from_channels',
        'schedule': crontab(minute=0, hour=0)
    }
}
app.conf.task_queues = (
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('normal', Exchange('normal'), routing_key='normal'),
)
app.conf.task_routes = {
    'tasks.send_activate_email': {'queue': 'high'},
    'task.send_recovery_email': {'queue': 'high'}
}
app.conf.task_default_queue = 'normal'
app.conf.task_default_exchange = 'normal'
app.conf.task_default_routing_key = 'normal'
app.conf.timezone = 'Europe/Moscow'


class DBTask(Task):
    def after_return(self, *args, **kwargs):
        db_session.remove()


@app.task(base=DBTask)
def get_videos_from_channels():
    channels = db_session.query(Channel).all()
    for channel in channels:
        channel_videos.delay(channel.id, channel.yt_id)


@app.task()
def send_activate_email(email, code):
    message = Mail(settings.EMAIL_FROM, email,
                   'Регистрация на edm.su',
                   f'Вы успешно зарегистрированы для активации аккаунта перейдите по ссылке: '
                   f'{settings.FRONTEND_URL}/user/activate/{code}')
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)
    return f'{email} отправлено письмо с активацией аккаунта'


@app.task()
def send_recovery_email(email, code):
    message = Mail(settings.EMAIL_FROM, email, 'Восстановление пароля на edm.su',
                   f'Для смены пароля перейдите по ссылке: {settings.FRONTEND_URL}/user/recovery/{code}')
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)
    return f'{email} отправлено письмо с восстановлением пароля'


@app.task(base=DBTask)
def channel_videos(channel_id, channel_yt_id, new_videos_count=0):
    videos = search_youtube_videos_from_channel(channel_yt_id)
    for video in videos:
        title = video['snippet']['title']
        slug = slugify(title, to_lower=True)
        date = parse(video['snippet']['publishedAt']).date()
        yt_id = video['id']
        yt_thumbnail = video['snippet']['thumbnails']['default']['url']
        duration = time_to_seconds(parse(video['contentDetails']['duration'][2:]).time())
        new_video = Video(title, slug, date, yt_id, yt_thumbnail, duration)
        new_video.channel_id = channel_id
        try:
            db_session.add(new_video)
            db_session.commit()
            new_videos_count += 1
        except IntegrityError:
            db_session.rollback()
    return f'Новых видео: {new_videos_count}'


@app.task(base=DBTask)
def add_all_videos_to_algolia():
    videos = db_session.query(Video).all()
    index = init_algolia_index()
    index.save_objects(
        [{'objectID': video.id, 'title': video.title, 'date': video.date, 'slug': video.slug,
          'thumbnail': video.yt_thumbnail} for video in videos])


def time_to_seconds(t: time):
    return (t.hour * 60 + t.minute) * 60 + t.second


def init_algolia_index():
    client = SearchClient.create(settings.ALGOLIA_APP_ID, settings.ALGOLIA_API_KEY)
    return client.init_index(settings.ALGOLIA_INDEX)


def search_youtube_videos_from_channel(channel,
                                       videos=None,
                                       next_page_token='',
                                       current_page=1,
                                       max_results=50,
                                       playlist_id=''):
    if not playlist_id:
        yt_channel = requests.get('https://www.googleapis.com/youtube/v3/channels',
                                  params={'part': 'contentDetails',
                                          'id': channel,
                                          'key': settings.YOUTUBE_API_KEY
                                          })
        yt_channel = yt_channel.json()
        playlist_id = yt_channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    if videos is None:
        videos = []
    yt_playlist_items = requests.get('https://www.googleapis.com/youtube/v3/playlistItems',
                                     params={'part': 'contentDetails',
                                             'playlistId': playlist_id,
                                             'maxResults': max_results,
                                             'pageToken': next_page_token,
                                             'key': settings.YOUTUBE_API_KEY
                                             })
    yt_playlist_items = yt_playlist_items.json()
    total_results = yt_playlist_items['pageInfo']['totalResults']
    yt_videos_ids = ','.join([item['contentDetails']['videoId'] for item in yt_playlist_items['items']])
    yt_videos = requests.get('https://www.googleapis.com/youtube/v3/videos',
                             params={'part': 'snippet,contentDetails',
                                     'id': yt_videos_ids,
                                     'key': settings.YOUTUBE_API_KEY
                                     })
    yt_videos = yt_videos.json()
    for video in yt_videos['items']:
        if parse(video['contentDetails']['duration'][2:]).time() > time(0, 20, 0):
            videos.append(video)
    if total_results > current_page * max_results:
        next_page_token = yt_playlist_items['nextPageToken']
        current_page += 1
        return search_youtube_videos_from_channel(channel,
                                                  videos,
                                                  next_page_token,
                                                  current_page,
                                                  playlist_id=playlist_id)
    return videos
