import googleapiclient.discovery
import googleapiclient.errors
from enum import Enum

from .base import BaseApi
from contentapi.helpers import normalize_params


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

    def list(self,
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
        response = request.execute()
        return response
