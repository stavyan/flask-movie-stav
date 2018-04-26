from flask import _app_ctx_stack as stack
import os
from pymongo import MongoClient
import redis as redispy
from werkzeug.local import LocalProxy


def _connect_mongo_db():
    if os.environ.get('MONGOHQ_URL'):
        c = MongoClient(os.environ['MONGOHQ_URL'])
        db = c.get_default_database()
    else:
        c = MongoClient()
        db = c.test

    return db


def _connect_redis():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    return redispy.from_url(redis_url)


def _get_mongo_db():
    ctx = stack.top
    if ctx is not None:
        if not hasattr(ctx, 'mongo_db'):
            ctx.mongo_db = _connect_mongo_db()
        return ctx.mongo_db


def _get_redis():
    ctx = stack.top
    if ctx is not None:
        if not hasattr(ctx, 'redis'):
            ctx.redis = _connect_redis()
        return ctx.redis

redis = LocalProxy(_get_redis)
mongo = LocalProxy(_get_mongo_db)