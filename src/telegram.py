import asyncio
import os
import re
from datetime import timezone, datetime

from events_manager import emit
from telethon import TelegramClient
from telethon.errors import RpcCallFailError, PeerIdInvalidError
from telethon.tl.types import PeerChannel

from src.crypto import is_token_account, get_symbol
from src.db import get_collection, tokens_collection_name, messages_collection_name
from src.events import NewAnalysysMessagesReceivedEvent, AnalysisStarted


class TelegramForwarder:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')

        self.client = TelegramClient('storage/session' + self.phone_number, self.api_id, self.api_hash)

    async def list_chats(self):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        dialogs = await self.client.get_dialogs()
        with open(f"storage/chats_of_{self.phone_number}.txt", "w", encoding="utf-8") as chats_file:
            for dialog in dialogs:
                print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
                chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")

        print("List of groups printed successfully!")

    async def send_message(self, chat_id, message):
        await self.client.send_message(chat_id, message)

    async def handle_token_source_message(self, analyzer_chat_id, source_chat_id, username_filter=None):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client.get_entity(PeerChannel(source_chat_id))
        except ValueError as e:
            print(f"Error retrieving entities for chat_id {source_chat_id}: {e}")
            return

        # Ottiene l'ultimo messaggio
        try:
            last_message_id = (await self.client.get_messages(source_entity, limit=1))[0].id
        except (RpcCallFailError, PeerIdInvalidError) as e:
            print(f"Error retrieving messages: {e}")
            return

        while True:
            try:
                messages = await self.client.get_messages(source_entity, min_id=last_message_id, limit=None)
            except (RpcCallFailError, PeerIdInvalidError) as e:
                print(f"Error retrieving messages: {e}")
                break

            for message in reversed(messages):
                if message.id == last_message_id:
                    break

                last_message_id = max(last_message_id, message.id)

                sender = await message.get_sender()
                if sender and username_filter and sender.username not in username_filter:
                    continue

                print(f"Message sent from: {sender.username}")

                for token in self.extract_tokens(message.text):
                    print(f"Token: {token}")

                    emit(AnalysisStarted(self, token, sender.username))

                    await self.client.send_message(analyzer_chat_id, f"/bundle {token[0]}")

                    print("Message forwarded")

                    await asyncio.sleep(5)

            await asyncio.sleep(5)

    @staticmethod
    def extract_tokens(message):
        contract_address_regex = r'\b[a-zA-Z0-9]{32,44}\b'
        result = set()

        result.update(re.findall(contract_address_regex, message))

        result = set(filter(lambda contract_address: is_token_account(contract_address), result))

        print(f"1{result}")

        result = set(map(lambda address: (address, get_symbol(address)), result))

        print(f"2{result}")

        result = set(filter(lambda token: token[1] is not None, result))

        print(f"3{result}")

        return result

    @staticmethod
    def extract_matched_symbols(symbol, message):
        symbol_regex = fr'\b[a-zA-Z0-9]{{{len(symbol)}}}\b'  # fixme: migliorare!!!
        result = set()

        result.update(re.findall(symbol_regex, message))

        result = set(filter(lambda x: x.upper() == symbol.upper(), result))

        print('symbolsss', result)

        return result

    async def handle_bonkbot_message(self, caller_chat_id):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        bonkbot_chat_id = -1002086003521  # Sostituisci con l'ID corretto o l'username del gruppo

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client.get_entity(PeerChannel(bonkbot_chat_id))
        except ValueError as e:
            print(f"Error retrieving entity for bonkbot")
            return

        # Ottiene l'ultimo messaggio
        try:
            last_message_id = (await self.client.get_messages(source_entity, limit=1))[0].id
        except (RpcCallFailError, PeerIdInvalidError) as e:
            print(f"Error retrieving messages: {e}")
            return

        while True:
            try:
                messages = await self.client.get_messages(source_entity, min_id=last_message_id,
                                                          limit=None)
            except (RpcCallFailError, PeerIdInvalidError) as e:
                print(f"Error retrieving messages: {e}")
                break

            for message in reversed(messages):
                if message.id == last_message_id:
                    break

                if message.text and '**🔥 BURNED LP 🔥**' in message.text and '**Open time:** `in' in message.text:
                    print(f"Message contains the phrase: {message.text}")

                    await self.client.send_message(caller_chat_id, message.text)
                    print("Message forwarded")

                    defi_solana_sniper_chat_id = 6661880210  # sniper tg bot
                    quote_amount = 0.0046

                    ca = message.text.split("**Mint:** `")[1].split("`")[0]
                    snipe_message = f"/snp {ca} {quote_amount}"
                    print(snipe_message)
                    await self.client.send_message(defi_solana_sniper_chat_id, snipe_message)
                    print("Snipe set")

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)

    async def handle_analyzer_message(self, analyzer_chat_id, token):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client.get_entity(PeerChannel(analyzer_chat_id))
        except ValueError as e:
            print(f"Error retrieving entity for bonkbot")
            return

        # Ottiene l'ultimo messaggio
        try:
            last_message_id = (await self.client.get_messages(source_entity, limit=1))[0].id
        except (RpcCallFailError, PeerIdInvalidError) as e:
            print(f"Error retrieving messages: {e}")
            return

        last_message_time = datetime.now(timezone.utc)

        new_messages = False

        while True:
            try:
                messages = await self.client.get_messages(source_entity, min_id=last_message_id,
                                                          limit=None)
            except (RpcCallFailError, PeerIdInvalidError) as e:
                print(f"Error retrieving messages: {e}")
                break

            for message in reversed(messages):
                if message.id == last_message_id:
                    break

                last_message_id = max(last_message_id, message.id)
                last_message_time = messages[0].date.replace(tzinfo=timezone.utc)

                if not message.text:
                    continue

                sender = await message.get_sender()

                if not sender:
                    continue

                ignore = [
                    'albertogferrario',
                    'dennozzz'
                ]

                if sender.username in ignore:
                    continue

                print(f"{sender.username}: analyzer message received")

                for symbol in self.extract_matched_symbols(token[1], message.raw_text):
                    new_messages = True

                    print(f"{symbol}: {token[0]}")
                    get_collection(tokens_collection_name).update_one(
                        {
                            "contract_address": token[0]
                        },
                        {
                            "$set": {
                                "contract_address": token[0],
                                "symbol": token[1],
                                "created_at": datetime.now()
                            }
                        },
                        upsert=True
                    )

                    get_collection(messages_collection_name).insert_one(
                        {
                            "message": message.text,
                            "username": sender.username,
                            "contract_address": token[0],
                            "created_at": datetime.now()
                        },
                    )

                    print('message data saved')
                    break

                if not message.buttons:
                    continue

                button_pressed = False
                buttons_to_press = [
                    'TRACK TEAM',
                    'Stop Tracking',
                ]

                for row in message.buttons:
                    for button in row:
                        for button_to_press in buttons_to_press:
                            if button_to_press.upper() in button.text.upper():  # fixme: approssimazione
                                await button.click()
                                button_pressed = True
                                break

                        if button_pressed:
                            break

                    if button_pressed:
                        break

            if ((datetime.now(timezone.utc) - last_message_time).total_seconds() / 60) == 5:  # fixme: timeout configurabile
                return

            if new_messages:
                emit(NewAnalysysMessagesReceivedEvent(self, token))
                new_messages = False

            await asyncio.sleep(60)
