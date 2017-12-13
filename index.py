import datetime
from flask import Flask, make_response
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from bson.json_util import dumps
from api.config import JWT_SECRET_KEY, CUSTOM_ERROR
from api.controllers.auth import Auth
from api.controllers.user import User
from api.core.response import Response


# -------------------------------- App initialization -------------------------------------
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})


# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(weeks=52)
jwt = JWTManager(app)


# handle_exception = app.handle_exception
# handle_user_exception = app.handle_user_exception

api = Api(app, catch_all_404s=True, errors=CUSTOM_ERROR)

# app.handle_exception = handle_exception
# app.handle_user_exception = handle_user_exception


# -------------------------------- Custom error handlers -------------------------------------
# TODO: Define custom error handlers for JWT


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
api.add_resource(Auth, '/auth', endpoint="auth")

api.add_resource(User, '/users', endpoint="users")
api.add_resource(User, '/users/<string:id>', endpoint="user")


if __name__ == '__main__':
    app.run(debug=False)
