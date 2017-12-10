import hashlib
from werkzeug.security import safe_str_cmp

from api.controllers.user import User
from api.core.mongo import Mongo


class UserJWT(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def authenticate(username, password):
    user = Mongo.db().users.find_one({'email': username})
    if user and safe_str_cmp(user['password'], hashlib.md5(password.encode('utf-8')).hexdigest()):
        return UserJWT(str(user['_id']), user['email'], user['password'])


def identity(payload):
    user_id = payload['identity']
    ctrl = User()
    return ctrl.get(user_id)

