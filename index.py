import datetime

from flask import Flask, make_response
from flask_restful import Api
from flask_cors import CORS
from bson.json_util import dumps

from api.config import JWT_SECRET_KEY, CUSTOM_ERROR
from api.controllers.user import User
from api.core.functions.auth import authenticate, identity
from api.core.response import Response
from flask_jwt import JWT, JWTError


# -------------------------------- App initialization -------------------------------------
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ALLOW_REFRESH'] = True
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(minutes=30)
app.config['JWT_REFRESH_EXPIRATION_DELTA'] = datetime.timedelta(weeks=1)


jwt = JWT(app, authenticate, identity)


handle_exception = app.handle_exception
handle_user_exception = app.handle_user_exception

api = Api(app, catch_all_404s=True, errors=CUSTOM_ERROR)

app.handle_exception = handle_exception
app.handle_user_exception = handle_user_exception


# -------------------------------- Custom error handlers -------------------------------------
def special_exception_handler(error):
    return output_json(data={"message": error.description}, code=401, headers={"Content-Type": "application/json"})


app.register_error_handler(JWTError, special_exception_handler)


# -------------------------------- Output handler/encoder -------------------------------------
@api.representation('application/json')
def output_json(data, code, headers=None):
    response = Response()
    response.setCode(code)

    if code == 200:
        response.setData(data)
    else:
        response.setError(data['message'])

    resp = make_response(dumps(response.get()), code)
    resp.headers.extend(headers or {})
    return resp


# -------------------------------- Routes -------------------------------------
api.add_resource(User, '/users', endpoint="users")
api.add_resource(User, '/users/<string:id>', endpoint="user")


if __name__ == '__main__':
    app.run(debug=False)
