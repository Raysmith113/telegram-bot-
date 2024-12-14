import asyncio
from telethon.sync import TelegramClient
from telethon.errors import RpcCallFailError, PeerIdInvalidError
from telethon.tl.types import PeerChannel, PeerChat, PeerUser

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client_list_chats = TelegramClient('session_list_chats_' + phone_number, api_id, api_hash)
        self.client_forward_messages = TelegramClient('session_forward_messages_' + phone_number, api_id, api_hash)

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

    async def forward_messages_to_channel(self, source_chat_id, destination_chat_id, phrase):
        await self.client_forward_messages.connect()

        if not await self.client_forward_messages.is_user_authorized():
            await self.client_forward_messages.send_code_request(self.phone_number)
            await self.client_forward_messages.sign_in(self.phone_number, input('Enter the code: '))

        # Tenta di ottenere l'entità del gruppo sorgente
        try:
            source_entity = await self.client_forward_messages.get_entity(PeerChannel(source_chat_id))
        except ValueError as e:
            print(f"Error retrieving entity for source chat ID {source_chat_id}: {e}")
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
                messages = await self.client_forward_messages.get_messages(source_entity, min_id=last_message_id, limit=None)
            except (RpcCallFailError, PeerIdInvalidError) as e:
                print(f"Error retrieving messages: {e}")
                break

            for message in reversed(messages):
                if message.text and '**🔥 BURNED LP 🔥**' in message.text and '**Open time:** `in' in message.text:
                    print(f"Message contains the phrase: {message.text}")
                    await self.client_forward_messages.send_message(destination_chat_id, message.text)
                    print("Message forwarded")

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
    source_chat_id = 2022757177  # Sostituisci con l'ID corretto o l'username del gruppo
    destination_chat_id = -4213378328  # Sostituisci con l'ID corretto o l'username del gruppo

    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        phrase = "Open time:"
        await forwarder.forward_messages_to_channel(source_chat_id, destination_chat_id, phrase)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
