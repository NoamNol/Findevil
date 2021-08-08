import googleapiclient.discovery
import googleapiclient.errors
from enum import Enum

from .base import BaseApi
from contentapi.helpers import normalize_params


class ParamPart(Enum):
    ID = 'id'
    REPLIES = 'replies'
    SNIPPET = 'snippet'


class ParamOrder(Enum):
    TIME = 'time'
    RELEVANCE = 'relevance'


class ParamTextFormat(Enum):
    HTML = 'html'
    PLAIN_TEXT = 'plainText'


class CommentThreads(BaseApi):
    '''
    YouTube CommentThreads api.
    See https://developers.google.com/youtube/v3/docs/commentThreads
    '''
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def list(self,
             part: set[ParamPart],
             max_results: int = None,
             order: ParamOrder = None,
             page_token: str = None,
             search_terms: str = None,
             text_format: ParamTextFormat = None,
             id: set[str] = None,
             video_id: str = None
             ):
        '''
        Returns a list of comment threads that match the API request parameters.
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
                'name': 'videoId',
                'value': video_id,
                'group': 'filter',
            },
            # Optional parameters
            {
                'name': 'maxResults',
                'value': max_results,
                'validator': (
                    'Acceptable values are 1 to 100',
                    lambda v: v >= 1 and v <= 100
                )
            },
            {
                'name': 'order',
                'value': order,
                'toString': lambda v: v.value,
            },
            {
                'name': 'pageToken',
                'value': page_token,
            },
            {
                'name': 'searchTerms',
                'value': search_terms,
            },
            {
                'name': 'textFormat',
                'value': text_format,
                'toString': lambda v: v.value,
                'default': ParamTextFormat.PLAIN_TEXT,
            },
        ]

        params = normalize_params(params_data)

        youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey=self.api_key)

        request = youtube.commentThreads().list(**params)
        response = request.execute()
        return response
