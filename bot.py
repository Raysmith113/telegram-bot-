import asyncio
import json
from asyncio import create_task
from datetime import datetime

from dotenv import load_dotenv
from events_manager import on

from src.ai import rank_token
from src.db import put_token_data, get_token_data, get_collection, messages_collection_name, tokens_collection_name
from src.events import TokenAnalyzedEvent
from src.telegram import TelegramForwarder

# Carica le variabili dal file .env
load_dotenv()

tokens_data = {}


@on(TokenAnalyzedEvent)
def save_token_data(event: TokenAnalyzedEvent):
    get_collection(tokens_collection_name).update_one(
        {
            "contract_address": event.contract_address
        },
        {
            "$set": {
                "contract_address": event.contract_address,
                "created_at": datetime.now()
            }
        },
        upsert=True
    )

    get_collection(messages_collection_name).update_one(
        {
            "contract_address": event.contract_address
        },
        {
            "$set": {
                "message": event.analyzer_message,
                "username": event.analyzer_username,
                "contract_address": event.contract_address,
                "created_at": datetime.now()
            }
        },
        upsert=True
    )

    print('message data saved')

    documents = get_collection(messages_collection_name).find({"contract_address": event.contract_address})

    all_documents_string = " | ".join(str(document['message']) for document in documents)

    # Stampa la stringa unica
    print(all_documents_string)

    score = json.loads(rank_token(all_documents_string))['score']
    print('score calculated: {}'.format(score))

    get_collection(tokens_collection_name).update_one({"contract_address": event.contract_address}, {"$set": {"score": score}})

    print('message data classified')


def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials file not found.")
        return None, None, None


def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")


async def main():
    # get_collection('messages').delete_many({})
    # get_collection('tokens').delete_many({})
    documents = get_collection('messages').find()
    print("Documenti trovati:")
    for document in documents:
        print(document)
    return
    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    choice = "2"

    if choice == "1":
        await forwarder.list_chats()

    elif choice == "2":
        # create_task(forwarder.handle_bonkbot_message())

        results = await asyncio.gather(create_task(forwarder.handle_genesis_gem_message()),
                                       create_task(forwarder.handle_analyzer_message()))

        for result in results:
            if isinstance(result, Exception):
                raise result

    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
