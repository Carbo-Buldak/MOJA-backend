from db import mongodb as db

from flask import request
from flask_restx import Resource, Namespace
from flask_jwt_extended import get_jwt_identity, jwt_required
import flask_bcrypt

from operator import itemgetter

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


@api.route('/video/<url>')
class TempStoredVideo(Resource):

    @jwt_required
    def patch(self, url):
        email = get_jwt_identity()['email']
        _json = request.get_json(silent=True)

        _json['subtitles'] = sorted(_json['subtitles'], key=itemgetter('playedTime'), reverse=True)

        if _json:
            db_response = db.users.update_one({'email': email, 'subtitling_videos.url': url},
                                              {'$set': {'subtitling_videos.1.subtitles': _json['subtitles']}})

            if db_response.modified_count == 1:
                db.videos.update_one({'url': url}, {'$set': {'status': 1}})
                return {'message': 'Temporary storing video saved successfully.'}, 200
            else:
                db_response = db.users.update_one({'email': email}, {'$push': {'subtitling_videos': _json}})
                if db_response.modified_count == 1:
                    return {'message': 'Temporary storing video saved successfully.'}, 200
                else:
                    return {'message': 'Failed to save temporary storing video.'}, 400
        else:
            return {'message': 'Bad request.'}, 400

    @jwt_required
    def get(self, url):
        email = get_jwt_identity()['email']

        video = db.users.find_one({'email': email, 'subtitling_videos.url': url}, {'subtitling_videos.$': 1, '_id': 0})
        if video:
            return {'video': video['subtitling_videos']}, 200
        else:
            return 'Failed to retrieve temporary stored video. This video may already have been subtitled.', 400
