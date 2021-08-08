from typing import Callable, Iterator


def api_pages_iterator(api_func: Callable, *args, **kwargs) -> Iterator:
    '''
    Iterate the api pages.
    Each page contains 'items' and may contain 'nextPageToken'.

    Note:
    'max_results' in kwargs will be removed from the api call,
    and used instead as the max number of items to return from all pages.
    If not specified, default to 999,999,999.
    '''
    max_items = kwargs.get('max_results') or 999_999_999
    items_count = 0
    api_kwargs = kwargs.copy()
    while items_count < max_items:
        api_kwargs['max_results'] = max_items - items_count
        err = None
        response = None
        try:
            response = api_func(*args, **api_kwargs)
        except Exception as e:
            err = e
        yield response, err
        if err or not response:
            break
        items = response.get('items')
        if isinstance(items, list):
            items_count += len(items)
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        else:
            api_kwargs['page_token'] = next_page_token
