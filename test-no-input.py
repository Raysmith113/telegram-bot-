import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client_list_chats = TelegramClient('session_list_chats_' + phone_number, api_id, api_hash)
        self.client_forward_messages = TelegramClient('session_forward_messages_' + phone_number, api_id, api_hash)

    async def list_chats(self):
        await self.client_list_chats.connect()

        # Ensure you're authorized
        if not await self.client_list_chats.is_user_authorized():
            await self.client_list_chats.send_code_request(self.phone_number)
            await self.client_list_chats.sign_in(self.phone_number, input('Enter the code: '))

        # Get a list of all the dialogs (chats)
        dialogs = await self.client_list_chats.get_dialogs()
        with open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8") as chats_file:
            # Print information about each chat
            for dialog in dialogs:
                print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
                chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")

        print("List of groups printed successfully!")

    async def forward_messages_to_channel(self, source_chat_id, destination_chat_id, phrase):
        await self.client_forward_messages.connect()

        # Ensure you're authorized
        if not await self.client_forward_messages.is_user_authorized():
            await self.client_forward_messages.send_code_request(self.phone_number)
            await self.client_forward_messages.sign_in(self.phone_number, input('Enter the code: '))

        last_message_id = (await self.client_forward_messages.get_messages(source_chat_id, limit=1))[0].id

        while True:
            print("Checking for messages and forwarding them...")
            # Get new messages since the last checked message
            messages = await self.client_forward_messages.get_messages(source_chat_id, min_id=last_message_id, limit=None)

            for message in reversed(messages):
                # Check if the message text includes the phrase in bold and "in"
                if message.text:
                    # Check for the  phrase "**🔥 BURNED LP 🔥**" "**Open time:**"
                    if '**🔥 BURNED LP 🔥**' in message.text and '**Open time:** `in' in message.text:
                        print(f"Message contains the phrase: {message.text}")

                        # Forward the message to the destination channel
                        await self.client_forward_messages.send_message(destination_chat_id, message.text)

                        print("Message forwarded")


                # Update the last message ID
                last_message_id = max(last_message_id, message.id)

            # Add a delay before checking for new messages again
            await asyncio.sleep(5)  # Adjust the delay time as needed


# Function to read credentials from file
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

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)

    # Hardcoded values for the script
    choice = "2"
    source_chat_id = 2022757177
    destination_chat_id = -4213378328

    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        phrase = "Open time:"  # This is the specific phrase we are looking for in bold
        await forwarder.forward_messages_to_channel(source_chat_id, destination_chat_id, phrase)
    else:
        print("Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())
