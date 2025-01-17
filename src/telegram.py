import asyncio
import os
import re

from events_manager import emit
from telethon import TelegramClient
from telethon.errors import RpcCallFailError, PeerIdInvalidError
from telethon.tl.types import PeerChannel

from src.events import TokenAnalyzedEvent

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
        with open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8") as chats_file:
            for dialog in dialogs:
                print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
                chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")

        print("List of groups printed successfully!")

    async def send_message(self, chat_id, message):
        await self.client.send_message(chat_id, message)

    async def handle_genesis_gem_message(self, analyzer_chat_id):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        genesis_gem_chat_id = -1002156987879  # fixme: -1002124901271

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client.get_entity(PeerChannel(genesis_gem_chat_id))
        except ValueError as e:
            print(f"Error retrieving entity for genesis gem: {e}")
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

                hot_usernames = [
                    'bitcoinbilliam'
                    'Oppkun',
                    'dave3xx',
                    'Vsanek3',
                    'tuanqu',
                    'CryptMonkk',
                    'Crypzypotela',
                    'ultrastarlife',
                    'dennozzz',  # fixme
                    'albertogferrario',  # fixme
                ]

                sender = await message.get_sender()

                if sender and sender.username in hot_usernames:
                    print(f"Message sent from: {sender.username}")

                    for contract_address in self.extract_contract_addresses(message.text):
                        print(f"Contract address: {contract_address}")

                        await self.client.send_message(analyzer_chat_id, f"/bundle {contract_address}")

                        print("Message forwarded")

                        await asyncio.sleep(5)

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)

    @staticmethod
    def extract_contract_addresses(message):
        # Regex per intercettare indirizzi di contratti (Ethereum ad esempio)
        contract_address_regex = r'\b[a-zA-Z0-9]{32,44}\b'
        result = set()

        result.update(re.findall(contract_address_regex, message))

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

    async def handle_analyzer_message(self, analyzer_chat_id):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        analyzer_peer = PeerChannel(analyzer_chat_id)

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client.get_entity(analyzer_peer)
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

                last_message_id = max(last_message_id, message.id)

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

                for contract_address in self.extract_contract_addresses(message.text):
                    emit(TokenAnalyzedEvent(self, contract_address, sender.username, message.text))
                    break  # fixme

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

            await asyncio.sleep(5)
