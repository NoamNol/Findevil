import os
from flaskr import app
from flask import request
from .bl import run_all


@app.route('/youtube/videos/<id>/comments', methods=['PUT'])
def scan_youtube_video_comments(id: str):
    max_items = request.args.get('max', None, int)
    API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    re = run_all(video_id=id, api_key=API_KEY, max_items=max_items)
    return {'res': re}, 202

    # TODO: Change this
    re = comments_api.list(
        part={comments.ParamPart.ID, comments.ParamPart.SNIPPET},
        id={id},
        max_results=10
    )
    return re, 202
