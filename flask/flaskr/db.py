import os
from flask import g
from pymongo import MongoClient, UpdateOne
from dataclasses import asdict

from flaskr import app
from models.youtube import YoutubeComment


def _get_db():
    if 'db' not in g:
        database = os.environ.get("MONGODB_DATABASE", '')
        username = os.environ.get("MONGODB_USERNAME", '')
        password = os.environ.get("MONGODB_PASSWORD", '')
        hostname = os.environ.get("MONGODB_HOSTNAME", '')
        port = os.environ.get("MONGODB_PORT", '')
        uri = f'mongodb://{username}:{password}@{hostname}:{port}/{database}'
        client = MongoClient(uri)
        g.db = client[database]
    return g.db


@app.teardown_appcontext
def _teardown_db(exception=None):
    '''
    Closes the db resource
    See https://flask.palletsprojects.com/en/2.0.x/appcontext/
    '''
    db = g.pop('db', None)
    if db:
        try:
            db.client.close()
        except Exception:
            pass


def _remove_none_keys(a_dict: dict):
    return {k: v for k, v in a_dict.items() if v is not None}


def _rename_dict_key(a_dict, old_key, new_key):
    a_dict[new_key] = a_dict.pop(old_key)


def _dataclass_to_dict(dataclass_obj, key_as_id: str = None):
    as_dict = asdict(dataclass_obj)
    as_dict = _remove_none_keys(as_dict)
    if key_as_id:
        _rename_dict_key(as_dict, key_as_id, '_id')
    return as_dict


def _insert_or_update_many(dict_list: list[dict], ordered: bool = True):
    db = _get_db()
    requests = [UpdateOne({'_id': d['_id']}, {'$set': d}, upsert=True) for d in dict_list]
    db.youtube.bulk_write(requests, ordered=ordered)


# ---------------- PUBLIC ----------------


def insert_many_youtube_comments(many_comments: list[YoutubeComment]):
    dict_list = [_dataclass_to_dict(d, key_as_id='comment_id') for d in many_comments]
    _insert_or_update_many(dict_list, ordered=False)
