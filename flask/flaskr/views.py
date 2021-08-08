import os
import time
from flaskr import app
from flask import request
from .bl import run_all


@app.route('/youtube/videos/<id>/comments', methods=['PUT'])
async def scan_youtube_video_comments(id: str):
    max_items = request.args.get('max', None, int)
    API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    start_time = time.perf_counter()
    try:
        await run_all(video_id=id, api_key=API_KEY, max_items=max_items)
        elapsed = time.perf_counter() - start_time
        return {"message": "Accepted", "time": elapsed}, 202
    except Exception:
        return {"message": "Failed"}, 500
