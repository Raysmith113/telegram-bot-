import asyncio
import json
import os
from asyncio import create_task
from datetime import datetime

from dotenv import load_dotenv
from events_manager import on

from src.ai import rank_token
from src.db import get_collection, messages_collection_name, tokens_collection_name, scores_collection_name
from src.events import NewAnalysysMessagesReceivedEvent, AnalysisStarted
from src.telegram import TelegramForwarder

load_dotenv()

analyzer_chat_id = int(os.getenv('ANALYZER_CHAT_ID'))
caller_chat_id = int(os.getenv('CALLER_CHAT_ID'))


@on(AnalysisStarted)
async def wait_analysis(event: AnalysisStarted):
    create_task(event.forwarder.handle_analyzer_message(analyzer_chat_id, event.token)),


@on(NewAnalysysMessagesReceivedEvent)
async def calculate_score(event: NewAnalysysMessagesReceivedEvent):
    documents = get_collection(messages_collection_name).find({"contract_address": event.token[0]})

    all_documents_string = " | ".join(str(document['message']) for document in documents)

    score = json.loads(rank_token(all_documents_string))['score']

    print('score calculated: {}'.format(score))

    await event.forwarder.send_message(
        caller_chat_id,
        f"{event.token[1]}\n`{event.token[0]}`\n\nScore: {score}",
    )

    get_collection(tokens_collection_name).update_one({"contract_address": event.token[0]},
                                                      {"$set": {"score": score}})

    get_collection(scores_collection_name).insert_one(
        {
            "contract_address": event.token[0],
            "created_at": datetime.now(),
            "score": score
        },
    )

    print('message data classified and score calculated')


async def main():
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
