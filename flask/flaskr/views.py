import os
from flaskr import app
from contentapi.youtube import comments


@app.route('/youtube/videos/<id>/comments', methods=['PUT'])
def scan_youtube_video_comments(id: str):
    API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    comments_api = comments.Comments(API_KEY)

    # TODO: Change this
    re = comments_api.list(
        part={comments.ParamPart.ID, comments.ParamPart.SNIPPET},
        id={id},
        max_results=10
    )
    return re, 202
