from enum import Enum


class ContentType(Enum):
    '''
    All types of content in Findevil.

    The value is the name of the corresponding table/collection in the db.
    '''
    YOUTUBE_COMMENT = 'youtube'
