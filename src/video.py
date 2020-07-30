from datetime import datetime

from db import mongodb as db
from db import get_all_document

from pymongo import DESCENDING

from flask import request
from flask_restx import Resource, Namespace
from flask_jwt_extended import get_jwt_identity, jwt_required

api = Namespace('video')


def change_date_format(document):
    document['date'] = document['date'].strftime('%Y.%m.%d')
    return document


@api.route('/')
class VideoList(Resource):

    def get(self):
        is_searching = request.args.get('searching', default=None)
        if is_searching == 'true':
            keyword = request.args.get('keyword')
            cursor = db.videos.find({'$text': {'$search': keyword}}, {'_id': 0})
            return {'videos': get_all_document(cursor, apply=change_date_format)}, 200
        else:
            items = int(request.args.get('items', default='16'))
            status = [0] if request.args.get('status') else [1, 2]
            sorting = request.args.get('sorting', default='date')
            skips = int(request.args.get('skips', default='0'))

            cursor = db.videos.find({'status': {'$in': status}},
                                    {'_id': 0}).sort(sorting, DESCENDING).skip(skips).limit(items)
            return {'videos': get_all_document(cursor, apply=change_date_format)}, 200

    @jwt_required
    def post(self):
        _json = request.get_json(silent=True)
        if _json:

            video = db.videos.find_one({'url': _json['url']})

            if video:
                db_response = db.videos.update_one({'_id': video['_id'], 'status': {'$ne': 2}}, {'$inc': {'count': 1}})
                if db_response.modified_count == 1:
                    return {'message': 'Updated video successfully'}, 200
                else:
                    return {'message': 'Failed to update existing video'}, 200
            else:
                _json['date'] = datetime.now()
                _json['status'] = 0
                _json['count'] = 1
                if db.videos.insert_one(_json):
                    return {'message': 'Created video successfully'}, 201
                else:
                    return {'message': 'Failed to create video.'}, 400
        else:
            return {'message': 'Bad request'}, 400


@api.route('/<url>')
class Video(Resource):

    def get(self, url):

        document = db.videos.find_one_and_update({'url': url}, {'$inc': {'count': 1}}, {'_id': 0})
        document['date'] = document['date'].strftime('%Y.%m.%d')

        if document:
            return {'video': document}, 200
        else:
            return {'message': 'Failed to retrieve video.'}, 400

    @jwt_required
    def patch(self, url):
        _json = request.get_json()
        if _json:
            email = get_jwt_identity()['email']

            user = db.users.find_one_and_update({'email': email}, {'$pull': {'subtitling_videos': {'url': url}},
                                                '$push': {'subtitled_videos': {'title': _json['title'], 'url': url}},
                                                '$inc': {'point': len(_json['subtitles'])}})

            nickname = user['nickname']

            db_response = db.videos.update_one({'url': url},
                                               {'$set': {'subtitles': _json['subtitles'], 'date': datetime.now(),
                                                         'author': nickname, 'status': 2}})
            if db_response.modified_count == 1:
                db.users.update({'subtitling_videos': {'$elemMatch': {'url': url}}},
                                {'$pull': {'subtitled_videos': {'url': url}}})
                return {'message': 'Updated video successfully'}, 200
            else:
                return {'message': 'Failed to update video'}, 400

        else:
            return {'message': 'Bad request'}, 400







