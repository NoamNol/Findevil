from glom import glom

from contentapi.youtube import comment_threads
from contentapi.youtube.youtube_helpers import api_pages_iterator


def run_all(video_id: str, api_key: str, max_items: int = None):
    return keep_all_video_comment_thread_ids(video_id, api_key, max_items)


def keep_all_video_comment_thread_ids(video_id: str, api_key: str, max_items: int = None):
    all_comment_thread_ids = []
    comment_threads_api = comment_threads.CommentThreads(api_key)
    pages_iterator = api_pages_iterator(
        comment_threads_api.list,
        max_results=max_items,
        part={comment_threads.ParamPart.ID},
        video_id=video_id,
    )
    for page, err in pages_iterator:
        if err:
            # TODO: handle error
            break
        page_ids: list[str] = glom(page, ('items', ['id']), default=[])
        if not page_ids:
            # TODO: log warning about empty page
            pass
        else:
            all_comment_thread_ids.extend(page_ids)
    return all_comment_thread_ids
