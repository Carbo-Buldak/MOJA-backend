from db import mongodb as db

from flask import request
from flask_restx import Resource, Namespace
from flask_jwt_extended import get_jwt_identity, jwt_required
import flask_bcrypt


api = Namespace('user')


@api.route('/')
class User(Resource):

    @jwt_required
    def get(self):
        email = get_jwt_identity()['email']

        user = db.users.find_one({'email': email}, {'_id': 0, 'password': 0})
        if user:
            return {'user': user}, 200
        else:
            return {'message': 'Failed to retrieve user'}, 400

    def post(self):
        _json = request.get_json(silent=True)
        if _json:
            if not db.users.find_one({'$or': [{'email': _json.get('email')}, {'nickname': _json.get('nickname')}]}):
                _json['password'] = flask_bcrypt.generate_password_hash(_json['password'])
                _json['point'] = 0
                _json['requested_videos'] = []
                _json['subtitling_videos'] = []
                _json['subtitled_videos'] = []
                db_response = db.users.insert_one(_json)
                if db_response.inserted_id:
                    return {'message': 'User created successfully.'}, 201
                else:
                    return {'message': 'Failed to create user.'}, 400
            else:
                return {'message': 'User already exists.'}, 409
        else:
            return {'message': 'Bad request.'}, 400

    @jwt_required
    def patch(self):
        email = get_jwt_identity()['email']
        _json = request.get_json(silent=True)

        if _json:
            db_response = db.users.update_one({'email': email}, {'$push': {'subtitling_videos': _json}})
            if db_response.modified_count == 1:
                return {'message': 'User updated successfully.'}, 201
            else:
                return {'message': 'Failed to update user.'}, 400
        else:
            return {'message': 'Bad request.'}, 400



