from functools import wraps
import httplib
import logging

from ac_flask.hipchat import installable
from ac_flask.hipchat.auth import require_tenant, tenant
import os
from flask import jsonify, request
from urlparse import urlparse


_log = logging.getLogger(__name__)


def _not_none(app, name, default):
    val = app.config.get(name, default)
    if val is not None:
        return val
    else:
        raise ValueError("Missing '{key}' configuration property".format(key=name))


class Addon(object):

    def __init__(self, app, key=None, name=None, description=None, config=None,
                 env_prefix="AC_", allow_room=True, allow_global=False,
                 scopes=None, vendor_name=None, vendor_url=None, avatar=None):
        if scopes is None:
            scopes = ['send_notification']

        if avatar is None:
            avatar_url = "https://abotars.hipch.at/bot/" + _not_none(app, 'ADDON_KEY', key) + ".png"
            avatar = {
                "url": avatar_url,
                "url@2x": avatar_url
            }

        self.app = app
        self._init_app(app, config, env_prefix)

        self.descriptor = {
            "key": _not_none(app, 'ADDON_KEY', key),
            "name": _not_none(app, 'ADDON_NAME', name),
            "description": app.config.get('ADDON_DESCRIPTION', description) or "",
            "links": {
                "self": self._relative_to_base("/addon/descriptor")
            },
            "capabilities": {
                "installable": {
                    "allowRoom": allow_room,
                    "allowGlobal": allow_global
                },
                "hipchatApiConsumer": {
                    "scopes": scopes,
                    "avatar": avatar
                }
            },
            "vendor": {
                "url": app.config.get('ADDON_VENDOR_URL', vendor_url) or "",
                "name": app.config.get('ADDON_VENDOR_NAME', vendor_name) or ""
            }
        }

        if app.config.get('BASE_URL') is not None and app.config.get('AVATAR_URL') is not None:
            self.descriptor['capabilities']['hipchatApiConsumer']['avatar'] = {
                'url': app.config.get('BASE_URL') + app.config.get('AVATAR_URL')
            }

        installable.init(addon=self,
                         allow_global=allow_global,
                         allow_room=allow_room)

        @self.app.route("/addon/descriptor")
        def descriptor():
            return jsonify(self.descriptor)

        self.app.route("/")(descriptor)

    @staticmethod
    def _init_app(app, config, env_prefix):
        app.config.from_object('ac_flask.hipchat.default_settings')
        if config is not None:
            app.config.from_object(config)

        if env_prefix is not None:
            env_vars = {key[len(env_prefix):]: val for key, val in os.environ.items()}
            app.config.update(env_vars)

        if app.config['DEBUG']:
            # These two lines enable debugging at httplib level (requests->urllib3->httplib)
            # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
            # The only thing missing will be the response.body which is not logged.
            httplib.HTTPConnection.debuglevel = 1

            # You must initialize logging, otherwise you'll not see debug output.
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        else:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.WARN)

        app.events = {}

    def configure_page(self, path="/configure", **kwargs):
        self.descriptor['capabilities'].setdefault('configurable', {})['url'] = self._relative_to_base(path)

        def inner(func):
            return self.app.route(rule=path, **kwargs)(require_tenant(func))

        return inner

    def webhook(self, event, name=None, pattern=None, path=None, auth="jwt", **kwargs):
        if path is None:
            path = "/event/" + event

        wh = {
            "event": event,
            "url": self._relative_to_base(path),
            "authentication": auth
        }
        if name is not None:
            wh['name'] = name

        if pattern is not None:
            wh['pattern'] = pattern
        self.descriptor['capabilities'].setdefault('webhook', []).append(wh)

        def inner(func):
            return self.app.route(rule=path, methods=['POST'], **kwargs)(require_tenant(func))

        return inner

    def route(self, anonymous=False, *args, **kwargs):
        """
        Decorator for routes with defaulted required authenticated tenants
        """
        def inner(func):
            if not anonymous:
                func = require_tenant(func)
            func = self.app.route(*args, **kwargs)(func)
            return func

        return inner

    def glance(self, key, name, target, icon, icon2x=None, conditions=None, anonymous=False, path=None, **kwargs):

        if path is None:
            path = "/glance/" + key

        if icon2x is None:
            icon2x = icon

        glance_capability = {
            "key": key,
            "name": {
                "value": name
            },
            "queryUrl": self._relative_to_base(path),
            "target": target,
            "icon": {
                "url": self._relative_to_base(icon),
                "url@2x": self._relative_to_base(icon2x)
            },
            "conditions": conditions or []
        }

        self.descriptor['capabilities'].setdefault('glance', []).append(glance_capability)

        def inner(func):
            return self.route(anonymous, rule=path, **kwargs)(self.cors(self.json_output(func)))

        return inner

    def webpanel(self, key, name, location="hipchat.sidebar.right", anonymous=False, path=None, **kwargs):

        if path is None:
            path = "/webpanel/" + key

        webpanel_capability = {
            "key": key,
            "name": {
                "value": name
            },
            "url": self._relative_to_base(path),
            "location": location
        }

        self.descriptor['capabilities'].setdefault('webPanel', []).append(webpanel_capability)

        def inner(func):
            return self.route(anonymous, rule=path, **kwargs)(func)

        return inner

    def cors(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            whitelisted_origin = self._get_white_listed_origin()
            installed_from = tenant.installed_from if tenant else None
            response = self.app.make_response(func(*args, **kwargs))
            response.headers['Access-Control-Allow-Origin'] = whitelisted_origin or installed_from or '*'
            return response
        return inner

    def json_output(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)
            return jsonify(res) if isinstance(res, dict) else res
        return inner

    def _relative_to_base(self, path):
        base = self.app.config['BASE_URL']
        path = '/' + path if not path.startswith('/') else path
        return base + path

    def _get_white_listed_origin(self):
        try:
            origin = request.headers['origin']
            if origin:
                origin_url = urlparse(origin)
                if origin_url and origin_url.hostname.endswith(self.app.config['CORS_WHITELIST']):
                    return origin
            return None
        except KeyError:
            return None

    def run(self, *args, **kwargs):
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            print("")
            print("--------------------------------------")
            print("Public descriptor base URL: %s" % self.app.config['BASE_URL'])
            print("--------------------------------------")
            print("")

        self.app.run(*args, **kwargs)
