import asyncio
import os
import sys
from glom import glom

from contentapi.youtube import comment_threads, comments
from contentapi.youtube.youtube_helpers import api_pages_iterator
from models.youtube import YoutubeComment
from . import db


async def scan_youtube_video_comments(video_id: str, api_key: str, max_items: int = None):
    WORKERS_NUM = int(os.environ.get('ASYNC_WORKERS', 10))
    if not max_items:
        max_items = 999_999_999
    shared_data = {'comments_count': 0, 'replies_count': 0, 'producer_alive': True}
    top_level_comment_queue = asyncio.Queue(maxsize=max_items or 0)

    # Start replies workers, they wait to get ids from the top_level_comment_queue,
    # fetch replies from the api and save to db
    replies_workers = [asyncio.create_task(_replies_worker(
        top_level_comment_queue, api_key, shared_data, max_items)) for _ in range(WORKERS_NUM)]

    # Read top level comments, save to db and fill the top_level_comment_queue
    await _get_all_top_level_comments(
        top_level_comment_queue, video_id, api_key, shared_data, max_items)
    shared_data['producer_alive'] = False

    await asyncio.gather(*replies_workers, return_exceptions=True)
    return shared_data['comments_count'], shared_data['replies_count']


# ---------------- PRIVATE ----------------


async def _get_all_top_level_comments(
    top_level_comment_queue: asyncio.Queue,
    video_id: str,
    api_key: str,
    shared_data: dict,
    max_items: int
):
    comment_threads_api = comment_threads.CommentThreads(api_key)
    pages_iterator = api_pages_iterator(
        comment_threads_api.list,
        max_results=max_items,
        part={
            comment_threads.ParamPart.ID,
            comment_threads.ParamPart.SNIPPET,
            comment_threads.ParamPart.REPLIES},
        order=comment_threads.ParamOrder.RELEVANCE,
        video_id=video_id,
    )
    async for items, err in pages_iterator:
        if err:
            print(err, file=sys.stderr)  # TODO: handle error
            break
        top_level_comments: list[YoutubeComment] = [comments.parse_api_comment(
            glom(item, 'snippet.topLevelComment')) for item in items]

        # Count how many replies each top_level_comment has
        replies_counts = [len(glom(item, 'replies.comments', default=[])) for item in items]

        if not top_level_comments:
            continue
        if shared_data['comments_count'] >= max_items:
            break

        # Limit the comments number to the number of comments left until max_items
        comments_left: int = max_items - shared_data['comments_count']
        top_level_comments_to_save = top_level_comments[:comments_left]
        shared_data['comments_count'] += len(top_level_comments_to_save)

        db.insert_many_youtube_comments(top_level_comments_to_save)

        # YouTube API returns CommentThread with only part of the full replies list,
        # so we can't save all replies at this point.
        # Therefore, we send the top comments to the queue to handle replies reading later.
        for tl_comment, replies_count in zip(top_level_comments_to_save, replies_counts):
            if replies_count > 0:
                await top_level_comment_queue.put((tl_comment.comment_id, tl_comment.video_id))


async def _get_all_comment_replies(
    comment_id: str,
    video_id: str,
    api_key: str,
    shared_data: dict,
    max_items: int
):
    comments_api = comments.Comments(api_key)
    pages_iterator = api_pages_iterator(
        comments_api.list,
        max_results=max_items,
        part={comments.ParamPart.ID, comments.ParamPart.SNIPPET},
        parent_id=comment_id,
    )
    async for items, err in pages_iterator:
        if err:
            print(err, file=sys.stderr)  # TODO: handle error
            break
        replies: list[YoutubeComment] = [comments.parse_api_comment(item) for item in items]

        # Add video_id field (youtube api omits the videoId from the replies)
        for r in replies:
            r.video_id = video_id

        if not replies:
            continue
        if shared_data['comments_count'] >= max_items:
            break

        # Limit the comments number to the number of comments left until max_items
        comments_left: int = max_items - shared_data['comments_count']
        replies_to_save = replies[:comments_left]
        shared_data['comments_count'] += len(replies_to_save)
        shared_data['replies_count'] += len(replies_to_save)

        db.insert_many_youtube_comments(replies_to_save)


async def _replies_worker(
    top_level_comment_queue: asyncio.Queue,
    api_key: str,
    shared_data: dict,
    max_items: int
):
    while shared_data['comments_count'] < max_items:
        try:
            comment_id, video_id = top_level_comment_queue.get_nowait()
            await _get_all_comment_replies(comment_id, video_id, api_key, shared_data, max_items)
            top_level_comment_queue.task_done()
        except asyncio.QueueEmpty:
            if shared_data['producer_alive']:
                await asyncio.sleep(0.2)
                continue
            else:
                break
