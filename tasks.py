import asyncio
from datetime import time

import requests
from asyncpg import UniqueViolationError
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init, worker_process_shutdown
from dateutil.parser import parse
from kombu import Queue, Exchange
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from slugify import slugify

from app import settings
from app.crud.channel import get_channels
from app.crud.video import add_video
from app.db import database

app = Celery('tasks')
app.conf.broker_url = f'{settings.REDIS_URL}/0'
app.conf.broker_transport_options = {'visibility_timeout': 3600}
app.conf.beat_schedule = {
    'add-new-videos-from-channels-every-day-in-midnight': {
        'task': 'sync.get_videos_from_channels',
        'schedule': crontab(hour=0, minute=0)
    }
}
app.conf.task_queues = (
    Queue('scanner', Exchange('scanner'), routing_key='scanner'),
    Queue('default', Exchange('default'), routing_key='default')
)
app.conf.task_routes = {
    'sync.get_videos_from_channels': {'queue': 'scanner'},
    'sync.channel_videos': {'queue': 'scanner'}
}
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'
app.conf.timezone = 'Europe/Moscow'


@worker_process_init.connect
def init_worker(**kwargs):
    async_run(database.connect)


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    async_run(database.disconnect)


def async_run(func, *args, **kwargs):
    event_loop = asyncio.get_event_loop()
    return event_loop.run_until_complete(func(*args, **kwargs))


@app.task(name='sync.get_videos_from_channels')
def get_videos_from_channels():
    channels = async_run(get_channels)
    for channel in channels:
        channel_videos.delay(channel['id'], channel['yt_id'])


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


@app.task(name='sync.channel_videos')
def channel_videos(channel_id, channel_yt_id, new_videos_count=0):
    videos = get_youtube_videos_from_channel(channel_yt_id)
    for video in videos:
        title = video['snippet']['title']
        slug = slugify(title, to_lower=True)
        date = parse(video['snippet']['publishedAt']).date()
        yt_id = video['id']
        yt_thumbnail = video['snippet']['thumbnails']['default']['url']
        duration = time_to_seconds(parse(video['contentDetails']['duration'][2:]).time())
        try:
            async_run(add_video, title=title, slug=slug, yt_id=yt_id, yt_thumbnail=yt_thumbnail, date=date,
                      channel_id=channel_id, duration=duration)
        except UniqueViolationError:
            pass
        else:
            new_videos_count += 1
    return f'Новых видео: {new_videos_count}'


def time_to_seconds(t: time):
    return (t.hour * 60 + t.minute) * 60 + t.second


def get_youtube_videos_from_channel(channel,
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
        return get_youtube_videos_from_channel(channel,
                                               videos,
                                               next_page_token,
                                               current_page,
                                               playlist_id=playlist_id)
    return videos
