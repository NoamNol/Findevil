import asyncio
from glom import glom

from contentapi.youtube import comment_threads, comments
from contentapi.youtube.youtube_helpers import api_pages_iterator
from .db import insert_many_comments

WORKERS_NUM = 13


async def run_all(video_id: str, api_key: str, max_items: int = None):
    if not max_items:
        max_items = 999_999_999
    shared_data = {'comments_count': 0}
    top_level_comment_queue = asyncio.Queue(maxsize=max_items or 0)

    # Start replies workers, they wait to get ids from the top_level_comment_queue,
    # fetch replies from the api and save content to db
    replies_workers = [asyncio.create_task(replies_worker(
        top_level_comment_queue, api_key, shared_data, max_items)) for _ in range(WORKERS_NUM)]

    # Read top level comments, save content to db and fill the top_level_comment_queue
    await get_all_top_level_comments(
        top_level_comment_queue, video_id, api_key, shared_data, max_items)
    await asyncio.gather(*replies_workers, return_exceptions=True)


async def get_all_top_level_comments(
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
        part={comment_threads.ParamPart.ID, comment_threads.ParamPart.SNIPPET},
        order=comment_threads.ParamOrder.RELEVANCE,
        video_id=video_id,
    )
    async for items, err in pages_iterator:
        if err:
            break  # TODO: handle error
        top_level_comments = [comments.parse_api_comment(
            glom(item, 'snippet.topLevelComment')) for item in items]
        if not top_level_comments:
            continue
        if shared_data['comments_count'] >= max_items:
            break
        comments_left: int = max_items - shared_data['comments_count']
        top_level_comments_to_send = top_level_comments[:comments_left]
        shared_data['comments_count'] += len(top_level_comments_to_send)

        # Save in db
        insert_many_comments(top_level_comments_to_send)

        # Send to queue
        for tl_comment in top_level_comments_to_send:
            await top_level_comment_queue.put(tl_comment.comment_id)


async def get_all_comment_replies(
    comment_id: str,
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
            break  # TODO: handle error
        replies = [comments.parse_api_comment(item) for item in items]
        if not replies:
            continue
        if shared_data['comments_count'] >= max_items:
            break
        comments_left: int = max_items - shared_data['comments_count']
        replies_to_send = replies[:comments_left]
        shared_data['comments_count'] += len(replies_to_send)

        # Save in db
        insert_many_comments(replies_to_send)


async def replies_worker(
    top_level_comment_queue: asyncio.Queue,
    api_key: str,
    shared_data: dict,
    max_items: int
):
    while shared_data['comments_count'] < max_items:
        comment_id = await top_level_comment_queue.get()
        await get_all_comment_replies(comment_id, api_key, shared_data, max_items)
        top_level_comment_queue.task_done()
