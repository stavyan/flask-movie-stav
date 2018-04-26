import json
import logging

from ac_flask.hipchat.events import events
from ac_flask.hipchat.db import mongo, redis
from .tenant import Tenant
from flask import request
import requests


_log = logging.getLogger(__name__)


def _invalid_install(msg):
    _log.error("Installation failed: %s" % msg)
    return msg, 400


def init(addon, allow_global, allow_room, send_events=True, db_name='clients', require_group_id=False):

    # noinspection PyUnusedLocal
    @addon.app.route('/addon/installable', methods=['POST'])
    def on_install():
        clients = mongo[db_name]
        data = json.loads(request.data)
        if not data.get('roomId', None) and not allow_global:
            return _invalid_install("This add-on can only be installed in individual rooms.  Please visit the " +
                                    "'Add-ons' link in a room's administration area and install from there.")

        if data.get('roomId', None) and not allow_room:
            return _invalid_install("This add-on cannot be installed in an individual room.  Please visit the " +
                                    "'Add-ons' tab in the 'Group Admin' area and install from there.")

        _log.info("Retrieving capabilities doc at %s" % data['capabilitiesUrl'])
        capdoc = requests.get(data['capabilitiesUrl'], timeout=10).json()

        if capdoc['links'].get('self', None) != data['capabilitiesUrl']:
            return _invalid_install("The capabilities URL %s doesn't match the resource's self link %s" %
                                    (data['capabilitiesUrl'], capdoc['links'].get('self', None)))

        client = Tenant(data['oauthId'], data['oauthSecret'], room_id=data.get('roomId', None), capdoc=capdoc)

        try:
            session = client.get_token(redis, token_only=False,
                                       scopes=addon.descriptor['capabilities']['hipchatApiConsumer']['scopes'])
        except Exception as e:
            _log.warn("Error validating installation by receiving token: %s" % e)
            return _invalid_install("Unable to retrieve token using the new OAuth information")

        _log.info("session: %s" % json.dumps(session))
        if require_group_id and int(require_group_id) != int(session['group_id']):
            _log.error("Attempted to install for group %s when group %s is only allowed" %
                       (session['group_id'], require_group_id))
            return _invalid_install("Only group %s is allowed to install this add-on" % require_group_id)

        client.group_id = session['group_id']
        client.group_name = session['group_name']
        clients.remove(client.id_query)
        clients.insert(client.to_map())
        if send_events:
            events.fire_event('install', {"client": client})
        return '', 201

    # noinspection PyUnusedLocal
    @addon.app.route('/addon/installable/<string:oauth_id>', methods=['DELETE'])
    def on_uninstall(oauth_id):
        uninstall_client(oauth_id, db_name, send_events)
        return '', 204

    addon.descriptor['capabilities']['installable']['callbackUrl'] = "{base}/addon/installable".format(
        base=addon.app.config['BASE_URL']
    )


def uninstall_client(oauth_id, db_name='clients', send_events=True):
    client = Tenant.load(oauth_id)
    clients = mongo[db_name]
    client_filter = {"id": oauth_id}
    clients.remove(client_filter)
    if send_events:
        events.fire_event('uninstall', {"client": client})