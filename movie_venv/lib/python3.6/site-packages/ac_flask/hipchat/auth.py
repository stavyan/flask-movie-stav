from ac_flask.hipchat.tenant import Tenant
from flask import _request_ctx_stack as stack, request
from flask import abort
import jwt
from werkzeug.local import LocalProxy
from functools import wraps


def require_tenant(func):

    @wraps(func)
    def inner(*args, **kwargs):
        if not tenant:
            abort(401)
        return func(*args, **kwargs)

    return inner


def _validate_jwt(req):
    if 'signed_request' in req.form:
        jwt_data = req.form['signed_request']
    else:
        jwt_data = req.args.get('signed_request', None)

    if not jwt_data:
        header = req.headers.get('authorization', '')
        jwt_data = header[4:] if header.startswith('JWT ') else None

    if not jwt_data:
        abort(401)

    try:
        oauth_id = jwt.decode(jwt_data, verify=False)['iss']
        client = Tenant.load(oauth_id)
        data = jwt.decode(jwt_data, client.secret, leeway=10)
        return client, data

    except jwt.DecodeError:
        abort(400)
    except jwt.ExpiredSignature:
        abort(401)


def _get_tenant():
    ctx = stack.top
    if ctx is not None:
        if not hasattr(ctx, 'tenant'):
            body = request.json
            cur_sender = cur_context = None
            if request.args.get('signed_request', None) or 'authorization' in request.headers:
                cur_tenant, data = _validate_jwt(request)
                cur_sender = User(data['sub'])
                cur_context = data.get('context', None)
            elif body and 'oauth_client_id' in body:
                tenant_id = body['oauth_client_id']
                cur_tenant = Tenant.load(tenant_id)
            else:
                cur_tenant = None

            if body and 'item' in body:
                sent_by = _extract_sender(body['item'])
                if sent_by:
                    user = User(user_id=sent_by['id'], name=sent_by['name'], mention_name=sent_by['mention_name'])
                    # Check if the sender in the webhook matches the one provided in the JWT
                    if cur_sender and str(cur_sender.id) != str(user.id):
                        abort(400)
                    cur_sender = user

            ctx.tenant = cur_tenant
            ctx.sender = cur_sender
            ctx.context = cur_context

        return ctx.tenant


def _extract_sender(item):
    if 'sender' in item:
        return item['sender']
    if 'message' in item and 'from' in item['message']:
        return item['message']['from']
    return None


def _get_sender():
    _get_tenant()
    if hasattr(stack.top, 'sender'):
        return stack.top.sender
    else:
        return None


def _get_context():
    _get_tenant()
    if hasattr(stack.top, 'context'):
        return stack.top.context
    else:
        return None


tenant = LocalProxy(_get_tenant)
sender = LocalProxy(_get_sender)
context = LocalProxy(_get_context)


class User(object):
    def __init__(self, user_id, name=None, mention_name=None):
        super(User, self).__init__()
        self.id = user_id
        self.name = name
        self.mention_name = mention_name
