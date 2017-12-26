import datetime
from flask import Flask, make_response, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from bson.json_util import dumps
from api.config import JWT_SECRET_KEY, CUSTOM_ERROR
from api.resources.auth import Auth
from api.resources.data_process import DataProcess
from api.resources.project import Project
from api.resources.recommendation import Recommendation
from api.resources.user import User
from api.core.response import Response


# -------------------------------- App initialization -------------------------------------
# Setup Flask app
app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Setup Cross Domain Requests
cors = CORS(app, resources={r"*": {"origins": "*"}})

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(weeks=52)
jwt = JWTManager(app)

# Setup Flask-RESTful
api = Api(app, catch_all_404s=True, errors=CUSTOM_ERROR)


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

api.add_resource(User, '/users/<string:id>/projects', endpoint="user_projects")

api.add_resource(Project, '/projects', endpoint="projects")

api.add_resource(DataProcess, '/dataprocess/<string:action>', endpoint="dataprocess")
api.add_resource(DataProcess, '/dataprocess/<string:project_id>/<string:action>', endpoint="get_data_sets")

api.add_resource(Recommendation, '/recommendation', endpoint="recommendation")

# -------------------------------- Application bootstrap -------------------------------------
if __name__ == '__main__':
    app.run()
