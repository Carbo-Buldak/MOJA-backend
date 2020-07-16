from pymongo import MongoClient
from src import config

client = MongoClient(config.config['mongodb'][0]['url'])
mongodb = client.MOJA

# mongodb.videos.create_index([('title', 'text')], name='search_index')


def get_all_document(cursor, apply=None):
    output = []
    for document in cursor:
        output.append(document)
    if apply:
        output = list(map(apply, output))
    return output
