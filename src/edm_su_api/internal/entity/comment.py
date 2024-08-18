from datetime import datetime

from pydantic import UUID4, Field

from edm_su_api.internal.entity.common import AttributeModel, BaseModel
from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import Video


class CommentBase(BaseModel):
    text: str = Field(max_length=120)


class NewCommentDto(CommentBase):
    user: User
    video: Video


class Comment(AttributeModel, CommentBase):
    id: int
    user_id: UUID4
    published_at: datetime
    video_id: int
