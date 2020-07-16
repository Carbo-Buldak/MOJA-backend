from src import config
from src.db import mongodb as db

import datetime

from flask import Flask, request, jsonify
from flask_restx import Api
from flask_jwt_extended import JWTManager, create_access_token
import flask_bcrypt

from src.user import api as user_api
from src.video import api as video_api

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.config['jwt'][0]['secret_key']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=10)
jwt = JWTManager(app)

@app.route('/api/signin')
def sign_in():
    _json = request.get_json(silent=True)
    if _json:
        user = db.users.find_one({'email': _json['email']}, {'_id': 0})
        if user and flask_bcrypt.check_password_hash(user['password'], _json['password']):
            del user['password']
            access_token = create_access_token(identity=_json)
            return jsonify({'token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    else:
        return jsonify({'message': 'Bad request parameters.'}), 400


api = Api(title='MOJA API', version='1.0', description='api for MOJA web application')
api.add_namespace(user_api, path='/api/user')
api.add_namespace(video_api, path='/api/video')



api.init_app(app)


if __name__ == '__main__':

    app.run(debug=True)
