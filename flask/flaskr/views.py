import os
import time
from flaskr import app
from flask import request
from . import bl


@app.route('/youtube/videos/<id>/comments', methods=['PUT'])
async def scan_youtube_video_comments(id: str):
    max_items = request.args.get('max', None, int)
    api_key = os.environ.get('YOUTUBE_API_KEY', '')
    start_time = time.perf_counter()
    try:
        comments_count, replies_count = await bl.scan_youtube_video_comments(
            video_id=id, api_key=api_key, max_items=max_items)
        elapsed = time.perf_counter() - start_time
        return {
            "message": "Accepted",
            "time": elapsed,
            'comments_count': comments_count,
            'replies_count': replies_count,
        }, 202
    except Exception:
        return {"message": "Failed"}, 500
