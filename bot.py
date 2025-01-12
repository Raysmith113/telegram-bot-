import asyncio
import os

from telethon.errors import RpcCallFailError, PeerIdInvalidError
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
import sqlite3


class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client_list_chats = TelegramClient('session_list_chats_' + phone_number, api_id, api_hash)
        self.client_forward_messages = TelegramClient('session_forward_messages_' + phone_number, api_id, api_hash)
        # self.sql_connection = self.init_database()

    @staticmethod
    def init_database():
        database_name = '.db'

        if not os.path.exists(database_name):
            print(f"Il database '{database_name}' non esiste. Creazione in corso...")

            # Crea e inizializza il database
            with sqlite3.connect(database_name) as conn:
                cursor = conn.cursor()

                # Esempio: creazione di una tabella di base
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                conn.commit()
                print(f"Il database '{database_name}' è stato creato con successo.")

        return sqlite3.connect(database_name)

    async def list_chats(self):
        await self.client_list_chats.connect()

        if not await self.client_list_chats.is_user_authorized():
            await self.client_list_chats.send_code_request(self.phone_number)
            await self.client_list_chats.sign_in(self.phone_number, input('Enter the code: '))

        dialogs = await self.client_list_chats.get_dialogs()
        with open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8") as chats_file:
            for dialog in dialogs:
                print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
                chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")

        print("List of groups printed successfully!")

    async def handle_genesis_gem_message(self, bonkbot_caller_chat_id):
        await self.client_forward_messages.connect()

        if not await self.client_forward_messages.is_user_authorized():
            await self.client_forward_messages.send_code_request(self.phone_number)
            await self.client_forward_messages.sign_in(self.phone_number, input('Enter the code: '))

        genesis_gem_chat_id = -1002124901271  # Sostituisci con l'ID corretto o l'username del gruppo

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client_forward_messages.get_entity(PeerChannel(genesis_gem_chat_id))
        except ValueError as e:
            print(f"Error retrieving entity for genesis gem: {e}")
            return

        # Ottiene l'ultimo messaggio
        try:
            last_message_id = (await self.client_forward_messages.get_messages(source_entity, limit=1))[0].id
            print(f"Last message ID: {last_message_id}")
        except (RpcCallFailError, PeerIdInvalidError) as e:
            print(f"Error retrieving messages: {e}")
            return

        while True:
            print("Checking for messages and forwarding them...")
            try:
                messages = await self.client_forward_messages.get_messages(source_entity, min_id=last_message_id,
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
                    'ultrastarlife'
                ]

                if message.from_user and message.from_user.username in hot_usernames:
                    print(f"Message sent from: {message.from_user.username}")

                    await self.client_forward_messages.send_message(bonkbot_caller_chat_id,
                                                                    f"{message.from_user.username}\n\n{message.text}")
                    print("Message forwarded")

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)

    async def handle_bonkbot_message(self, bonkbot_caller_chat_id):
        await self.client_forward_messages.connect()

        if not await self.client_forward_messages.is_user_authorized():
            await self.client_forward_messages.send_code_request(self.phone_number)
            await self.client_forward_messages.sign_in(self.phone_number, input('Enter the code: '))

        bonkbot_chat_id = -1002086003521  # Sostituisci con l'ID corretto o l'username del gruppo

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client_forward_messages.get_entity(PeerChannel(bonkbot_chat_id))
        except ValueError as e:
            print(f"Error retrieving entity for bonkbot")
            return

        # Ottiene l'ultimo messaggio
        try:
            last_message_id = (await self.client_forward_messages.get_messages(source_entity, limit=1))[0].id
            print(f"Last message ID: {last_message_id}")
        except (RpcCallFailError, PeerIdInvalidError) as e:
            print(f"Error retrieving messages: {e}")
            return

        while True:
            print("Checking for messages and forwarding them...")
            try:
                messages = await self.client_forward_messages.get_messages(source_entity, min_id=last_message_id,
                                                                           limit=None)
            except (RpcCallFailError, PeerIdInvalidError) as e:
                print(f"Error retrieving messages: {e}")
                break

            for message in reversed(messages):
                if message.id == last_message_id:
                    break

                if message.text and '**🔥 BURNED LP 🔥**' in message.text and '**Open time:** `in' in message.text:
                    print(f"Message contains the phrase: {message.text}")

                    await self.client_forward_messages.send_message(bonkbot_caller_chat_id, message.text)
                    print("Message forwarded")

                    defi_solana_sniper_chat_id = 6661880210  # sniper tg bot
                    quote_amount = 0.0046

                    ca = message.text.split("**Mint:** `")[1].split("`")[0]
                    snipe_message = f"/snp {ca} {quote_amount}"
                    print(snipe_message)
                    await self.client_forward_messages.send_message(defi_solana_sniper_chat_id, snipe_message)
                    print("Snipe set")

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)


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
        bonkbot_caller_chat_id = -1002156987879  # Sostituisci con l'ID corretto o l'username del gruppo

        await forwarder.handle_genesis_gem_message(bonkbot_caller_chat_id)

        # await forwarder.handle_bonkbot_message(bonkbot_caller_chat_id)

    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
