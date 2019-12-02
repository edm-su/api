from datetime import time
from os import getenv

import requests
from celery import Celery, Task
from celery.schedules import crontab
from dateutil.parser import parse
from kombu import Queue, Exchange
from slugify import slugify
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Channel, Video, Dj

app = Celery('tasks')
app.conf.broker_url = 'redis://redis:6379/0'
app.conf.broker_transport_options = {'visibility_timeout': 3600}
app.conf.beat_schedule = {
    'add-new-videos-from-channels-every-day-in-midnight': {
        'task': 'tasks.get_videos_from_channels',
        'schedule': crontab(minute=0, hour=0)
    },
    'add-djs-to-videos-every-day-in-6-hours': {
        'task': 'tasks.get_videos_from_channels',
        'schedule': crontab(minute=0, hour=6)
    }
}
app.conf.task_queues = (
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('normal', Exchange('normal'), routing_key='normal'),
)
app.conf.task_default_queue = 'normal'
app.conf.task_default_exchange = 'normal'
app.conf.task_default_routing_key = 'normal'
app.conf.timezone = 'Europe/Moscow'


class DBTask(Task):
    def after_return(self, *args, **kwargs):
        SessionLocal.remove()


@app.task(base=DBTask)
def get_videos_from_channels():
    channels = SessionLocal.query(Channel).all()
    for channel in channels:
        channel_videos.delay(channel.id, channel.youtube_id)


@app.task(base=DBTask)
def add_djs_to_videos():
    djs = SessionLocal.query(Dj).all()
    for dj in djs:
        videos = SessionLocal.query(Video).filter(Video.title.like(f'%{dj.name}%'))
        for video in videos:
            if dj not in video.djs:
                video.djs.append(dj)
                SessionLocal.commit()


@app.task(base=DBTask)
def channel_videos(channel_id, channel_yt_id, new_videos_count=0):
    videos = search_youtube_videos_from_channel(channel_yt_id)
    for video in videos:
        title = video['snippet']['title']
        slug = slugify(title, to_lower=True)
        date = parse(video['snippet']['publishedAt']).date()
        yt_id = video['id']
        new_video = Video(title, slug, date, yt_id)
        new_video.channel_id = channel_id
        try:
            SessionLocal.add(new_video)
            SessionLocal.commit()
            new_videos_count += 1
        except IntegrityError:
            SessionLocal.rollback()
    return f'Новых видео: {new_videos_count}'


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
                                          'key': getenv('YOUTUBE_API_KEY')
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
                                             'key': getenv('YOUTUBE_API_KEY')
                                             })
    yt_playlist_items = yt_playlist_items.json()
    total_results = yt_playlist_items['pageInfo']['totalResults']
    yt_videos_ids = ','.join([item['contentDetails']['videoId'] for item in yt_playlist_items['items']])
    yt_videos = requests.get('https://www.googleapis.com/youtube/v3/videos',
                             params={'part': 'snippet,contentDetails',
                                     'id': yt_videos_ids,
                                     'key': getenv('YOUTUBE_API_KEY')
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
