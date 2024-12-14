import asyncio
from telethon.sync import TelegramClient

# Leggi le credenziali dal file
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

async def get_chat_id_from_link(api_id, api_hash, phone_number, chat_link):
    client = TelegramClient('session_' + phone_number, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))

    # Estrarre la parte del nome utente dalla chat
    if "https://t.me/" in chat_link:
        chat_link = chat_link.replace("https://t.me/", "")
        if "/" in chat_link:
            chat_link = chat_link.split("/")[0]

    try:
        chat = await client.get_entity(chat_link)
        print(f"Chat ID for {chat_link} is {chat.id}")
        await client.disconnect()
        return chat.id
    except Exception as e:
        print(f"Failed to get chat ID from link: {e}")
        await client.disconnect()
        return None

async def main():
    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        with open("credentials.txt", "w") as file:
            file.write(api_id + "\n")
            file.write(api_hash + "\n")
            file.write(phone_number + "\n")

    chat_link = input("Enter the chat link: ")
    await get_chat_id_from_link(api_id, api_hash, phone_number, chat_link)

if __name__ == "__main__":
    asyncio.run(main())
