import googleapiclient.discovery
import googleapiclient.errors
import asyncio
from enum import Enum
from glom import glom

from .base import BaseApi
from contentapi.helpers import normalize_params
from models.youtube import YoutubeComment


class ParamPart(Enum):
    ID = 'id'
    SNIPPET = 'snippet'


class ParamTextFormat(Enum):
    HTML = 'html'
    PLAIN_TEXT = 'plainText'


class Comments(BaseApi):
    '''
    YouTube Comments api.
    See https://developers.google.com/youtube/v3/docs/comments
    '''
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    async def list(
        self,
        part: set[ParamPart],
        max_results: int = None,
        page_token: str = None,
        text_format: ParamTextFormat = None,
        id: set[str] = None,
        parent_id: str = None
    ):
        '''
        Returns a list of comments that match the API request parameters.
        '''
        params_data = [
            # Required parameters
            {
                'name': 'part',
                'value': part,
                'toString': lambda v: ','.join([p.value for p in v]),
            },
            # Filter parameters
            {
                'name': 'id',
                'value': id,
                'toString': lambda v: ','.join(v),
                'group': 'filter',
            },
            {
                'name': 'parentId',
                'value': parent_id,
                'group': 'filter',
            },
            # Optional parameters
            {
                'name': 'maxResults',
                'value': max_results,
                'middleware': lambda v: min(v, 100),
                'validator': (
                    'Acceptable values are 1 to 100',
                    lambda v: v >= 1 and v <= 100
                )
            },
            {
                'name': 'pageToken',
                'value': page_token,
            },
            {
                'name': 'textFormat',
                'value': text_format,
                'toString': lambda v: v.value,
                'default': ParamTextFormat.PLAIN_TEXT
            },
        ]

        params = normalize_params(params_data)

        youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey=self.api_key)

        request = youtube.comments().list(**params)
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, request.execute)
        response = await future
        return response


def parse_api_comment(api_comment: dict) -> YoutubeComment:
    if not api_comment:
        api_comment = {}
    yc = YoutubeComment(
        comment_id=api_comment.get('id', ''),
        video_id=glom(api_comment, 'snippet.videoId', default=''),
        text_original=glom(api_comment, 'snippet.textOriginal', default=''),
        parent_id=glom(api_comment, 'snippet.parentId', default=''),
        author_channel_id=glom(api_comment, 'snippet.authorChannelId.value', default=''),
        like_count=glom(api_comment, 'snippet.likeCount', default=0),
        published_at=glom(api_comment, 'snippet.publishedAt', default=''),
        updated_at=glom(api_comment, 'snippet.updatedAt', default=''),
    )
    return yc
