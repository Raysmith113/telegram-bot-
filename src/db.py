import os
from datetime import datetime

from pymongo import MongoClient

tokens_collection_name = 'tokens'
messages_collection_name = 'messages'
client = MongoClient(os.getenv('MONGO_URL'))


def get_collection(collection_name):
    db = client.mydatabase
    return db[collection_name]


def get_token_data(contract_address):
    documents = get_collection(messages_collection_name).findOne(contract_address)

    print("Documenti trovati:")
    for document in documents:
        print(document)


def put_token_data(contract_address, username, message):
    document = {
        "message": message,
        "username": username,
        "contract_address": contract_address,
        "created_at": datetime.now()  # Salva l'ora corrente come ISODate
    }

    return get_collection(messages_collection_name).insert_one(document)
