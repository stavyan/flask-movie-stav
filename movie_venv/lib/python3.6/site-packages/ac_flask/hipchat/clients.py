import json
from ac_flask.hipchat.auth import tenant
from ac_flask.hipchat.db import redis
import requests


def post(url, data, token):
    return requests.post(url, headers={
        "authorization": "Bearer %s" % token,
        "content-type": "application/json"
    }, data=json.dumps(data), timeout=10)


class RoomClient(object):
    @staticmethod
    def send_notification(message):
        token = tenant.get_token(redis)
        return post("%s/room/%s/notification" % (tenant.api_base_url, tenant.room_id), {"message": message}, token)


room_client = RoomClient()


class AddOnClient(object):
    @staticmethod
    def update_global_glance(glance_key, glance_data):
        token = tenant.get_token(redis, scopes=['view_group'])
        return post("%s/addon/ui" % tenant.api_base_url, {
            "glance": [
                {"content": glance_data, "key": glance_key}
            ]
        }, token)

    @staticmethod
    def update_room_glance(glance_key, glance_data, room_id):
        token = tenant.get_token(redis, scopes=['view_room'])
        return post("%s/addon/ui/room/%s" % (tenant.api_base_url, room_id), {
            "glance": [
                {"content": glance_data, "key": glance_key}
            ]
        }, token)

    @staticmethod
    def update_user_glance(glance_key, glance_data, user_id):
        token = tenant.get_token(redis, scopes=['view_group'])
        return post("%s/addon/ui/user/%s" % (tenant.api_base_url, user_id), {
            "glance": [
                {"content": glance_data, "key": glance_key}
            ]
        }, token)


addon_client = AddOnClient()