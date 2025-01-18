import asyncio
import json
import os
from asyncio import create_task
from datetime import datetime

from dotenv import load_dotenv
from events_manager import on

from src.ai import rank_token
from src.db import get_collection, messages_collection_name, tokens_collection_name
from src.events import TokenAnalyzedEvent
from src.telegram import TelegramForwarder

load_dotenv()

analyzer_chat_id = int(os.getenv('ANALYZER_CHAT_ID'))
caller_chat_id = int(os.getenv('CALLER_CHAT_ID'))


@on(TokenAnalyzedEvent)
async def save_token_data(event: TokenAnalyzedEvent):
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

    get_collection(messages_collection_name).insert_one(
        {
            "message": event.analyzer_message,
            "username": event.analyzer_username,
            "contract_address": event.contract_address,
            "created_at": datetime.now()
        },
    )

    print('message data saved')

    documents = get_collection(messages_collection_name).find({"contract_address": event.contract_address})

    all_documents_string = " | ".join(str(document['message']) for document in documents)

    # Stampa la stringa unica
    print(f"EVALUATING... | {all_documents_string}")

    score = json.loads(rank_token(all_documents_string))['score']

    print('score calculated: {}'.format(score))

    await event.forwarder.send_message(
        caller_chat_id,
        f"New contract evaluation: {event.contract_address}. Score: {score}"
    )

    get_collection(tokens_collection_name).update_one({"contract_address": event.contract_address},
                                                      {"$set": {"score": score}})

    print('message data classified')


async def main():
    # get_collection('messages').delete_many({})
    # get_collection('tokens').delete_many({})

    documents = get_collection('messages').find()
    print("Documenti trovati:")
    for document in documents:
        print(document)

    forwarder = TelegramForwarder()

    choice = "2"

    if choice == "1":
        await forwarder.list_chats()

    elif choice == "2":
        tasks = [
            # create_task(forwarder.handle_bonkbot_message(caller_chat_id))
            # create_task(forwarder.handle_token_source_message(analyzer_chat_id, -1002124901271, [
            #     'bitcoinbilliam'
            #     'Oppkun',
            #     'dave3xx',
            #     'Vsanek3',
            #     'tuanqu',
            #     'CryptMonkk',
            #     'Crypzypotela',
            #     'ultrastarlife',
            # ])),  # genesis gem
            create_task(forwarder.handle_token_source_message(analyzer_chat_id, -1002433791139)),  # analyzer solo
            create_task(forwarder.handle_analyzer_message(analyzer_chat_id)),
        ]

        print("Forwarder starter, waiting messages...")

        results = await asyncio.gather(*tasks)

        for result in results:
            if isinstance(result, Exception):
                raise result

    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
