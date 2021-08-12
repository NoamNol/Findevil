from dataclasses import dataclass
from typing import Optional


@dataclass
class YoutubeComment:
    comment_id: str
    video_id: str
    text_original: str
    parent_id: Optional[str]
    author_channel_id: str
    like_count: int
    published_at: str
    updated_at: str
