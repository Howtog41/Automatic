import asyncio
from telegram.ext import ApplicationBuilder

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = -1001984768732  # Replace with source channel ID (include -100 prefix if private)

async def fetch_messages(application):
    try:
        bot = application.bot
        messages = []
        print("Fetching messages...")

        # Fetch the latest 50 messages from the channel
        async for message in bot.iter_chat_messages(chat_id=SOURCE_CHANNEL_ID, limit=50):
            if message.text:  # Only consider text messages
                messages.append(message.text)

        print(f"Fetched {len(messages)} messages:")
        for msg in messages:
            print(msg)  # Print each fetched message
        return messages
    except Exception as e:
        print(f"Error while fetching messages: {e}")

async def main():
    # Build application
    app = ApplicationBuilder().token(API_TOKEN).build()

    # Fetch messages
    await fetch_messages(app)

if __name__ == "__main__":
    asyncio.run(main())
