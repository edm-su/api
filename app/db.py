import databases
import sqlalchemy

from app import settings
from app.helpers import generate_secret_code

if settings.TEST:
    database = databases.Database(settings.DATABASE_URL, force_rollback=True)
else:
    database = databases.Database(settings.DATABASE_URL)

metadata = sqlalchemy.MetaData()

channels = sqlalchemy.Table(
    'channels',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('slug', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('yt_id', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('yt_thumbnail', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('yt_banner', sqlalchemy.String),
)

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('username', sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column('email', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('password', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean, server_default='f'),
    sqlalchemy.Column('activation_code', sqlalchemy.String(10), default=generate_secret_code),
    sqlalchemy.Column('recovery_code', sqlalchemy.String(10)),
    sqlalchemy.Column('recovery_code_lifetime_end', sqlalchemy.DateTime),
    sqlalchemy.Column('is_admin', sqlalchemy.Boolean, server_default='f'),
    sqlalchemy.Column('is_banned', sqlalchemy.Boolean, server_default='f'),
    sqlalchemy.Column('created', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now()),
    sqlalchemy.Column('last_login', sqlalchemy.DateTime),
    sqlalchemy.Column('last_login_ip', sqlalchemy.String),
)

posts = sqlalchemy.Table(
    'posts',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('annotation', sqlalchemy.String),
    sqlalchemy.Column('text', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('slug', sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column('published_at', sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column('thumbnail', sqlalchemy.String),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
)

videos = sqlalchemy.Table(
    'videos',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('slug', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('date', sqlalchemy.Date),
    sqlalchemy.Column('yt_id', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('yt_thumbnail', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('channel_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('channels.id')),
    sqlalchemy.Column('duration', sqlalchemy.Integer, server_default="0"),
    sqlalchemy.Column('deleted', sqlalchemy.Boolean, server_default='f'),
    sqlalchemy.Index('title_idx', 'title', postgresql_ops={'title': 'gin_trgm_ops'}, postgresql_using='gin'),
)

liked_videos = sqlalchemy.Table(
    'liked_videos',
    metadata,
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('video_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('videos.id')),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime, server_default=sqlalchemy.sql.func.now()),
    sqlalchemy.UniqueConstraint('user_id', 'video_id', name='unique_liked_video'),
)

comments = sqlalchemy.Table(
    'comments',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'),
                      nullable=False),
    sqlalchemy.Column('text', sqlalchemy.Text, nullable=False),
    sqlalchemy.Column('published_at', sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now()),
    sqlalchemy.Column('deleted', sqlalchemy.Boolean, server_default='f'),
    sqlalchemy.Column('video_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('videos.id', ondelete='CASCADE'),
                      nullable=False)
)
