from pyrogram import Client

# Telegram API credentials
API_ID = '15502786'  # Replace with your API ID
API_HASH = 'bb32e00647b1bfe66e6cd298a2c66a5a'  # Replace with your API Hash
BOT_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'  # Replace with your bot token

# Source channel information
SOURCE_CHANNEL = "-1001984768732"  # Replace with source channel username or ID

# Create Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def fetch_messages():
    async with app:
        print("Fetching messages...")
        messages = []
        async for message in app.get_chat_history(SOURCE_CHANNEL, limit=50):
            if message.text:
                messages.append(message.text)
        
        print(f"Fetched {len(messages)} messages:")
        for msg in messages:
            print(msg)  # Print fetched messages
        return messages

if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_messages())
