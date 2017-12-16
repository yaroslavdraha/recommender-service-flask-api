import datetime
from bson.json_util import dumps
from flask import Flask, make_response, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mongoalchemy import MongoAlchemy
from flask_restful import Api

from api.config import JWT_SECRET_KEY, CUSTOM_ERROR, DB_NAME, DB_PORT, DB_HOST, DB_USER, DB_PASS

from api.core.response import Response



# -------------------------------- App initialization -------------------------------------
# Main app
app = Flask(__name__)

app.config['MONGOALCHEMY_DATABASE'] = DB_NAME
app.config['MONGOALCHEMY_SERVER_AUTH'] = False
app.config["MONGOALCHEMY_PORT"] = DB_PORT
app.config["MONGOALCHEMY_SERVER"] = DB_HOST
app.config["MONGOALCHEMY_USER"] = DB_USER
app.config["MONGOALCHEMY_PASSWORD"] = DB_PASS







# Cross Origin Requests support
cors = CORS(app, resources={r"*": {"origins": "*"}})

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(weeks=52)
jwt = JWTManager(app)

# Setup Flask-RESTful
api = Api(app, catch_all_404s=True, errors=CUSTOM_ERROR)

db = MongoAlchemy(app)
# Setup MONGODB connection


from api.resources.auth import Auth
from api.models.user import UserModel
from api.resources.user import UserResource


# -------------------------------- Custom error handlers -------------------------------------
@jwt.unauthorized_loader
def unauthorized_request(message):
    response = Response()
    response.setError(message)
    return jsonify(response.get())


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

api.add_resource(UserResource, '/users', endpoint="users")
api.add_resource(UserResource, '/users/<string:id>', endpoint="user")


if __name__ == '__main__':
    app.run(debug=False)
