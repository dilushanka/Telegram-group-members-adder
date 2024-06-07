from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import time

# Replace 'API_ID' and 'API_HASH' with your actual API ID and API Hash
api_id = 'Your-API-ID'
api_hash = 'You-API-hash'
phone = 'Phone-Number'  # Include country code, e.g., +123456789

client = TelegramClient(phone, api_id, api_hash)

async def main():
    await client.start()

    # Get dialogs
    dialogs = await client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=200,
        hash=0
    ))

    # Print out all dialogs
    for i, chat in enumerate(dialogs.chats):
        print(f"{i}. {chat.title} ({chat.id})")

    # Choose source group
    source_group_index = int(input("Enter the number of the source group: "))
    source_group = dialogs.chats[source_group_index]

    # Choose destination group
    destination_group_index = int(input("Enter the number of the destination group: "))
    destination_group = dialogs.chats[destination_group_index]

    # Get all participants from the source group
    source_participants = await client.get_participants(source_group)

    # Get all participants from the destination group
    destination_participants = await client.get_participants(destination_group)
    destination_participant_ids = {user.id for user in destination_participants}

    # Add participants to the destination group
    for user in source_participants:
        if user.id not in destination_participant_ids:
            retries = 0
            while retries < 5:  # Limit the number of retries
                try:
                    await client(InviteToChannelRequest(destination_group, [user]))
                    print(f"Added {user.id} to {destination_group.title}")
                    time.sleep(5)  # Avoid hitting limits
                    break
                except Exception as e:
                    print(f"Failed to add {user.id}: {e}")
                    retries += 1
                    backoff_time = 5 * (2 ** retries)  # Exponential backoff
                    print(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
        else:
            print(f"User {user.id} is already in {destination_group.title}")

with client:
    client.loop.run_until_complete(main())