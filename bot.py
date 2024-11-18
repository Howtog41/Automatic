import asyncio
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '-1001984768732'
DESTINATION_CHANNEL_ID = '-1002115327472'

bot = Bot(token=API_TOKEN)
scheduler = AsyncIOScheduler()
messages = []  # Store messages


async def fetch_messages():
    global messages
    print("Fetching messages...")
    try:
        # Fetch the last 100 messages from the source channel
        chat_history = await bot.get_chat_history(chat_id=SOURCE_CHANNEL_ID, limit=100)
        for message in chat_history:
            if message.text:  # Check if the message has text content
                messages.append(message.text)
        print(f"Fetched {len(messages)} messages.")
    except Exception as e:
        print(f"Error in fetch_messages: {e}")


async def post_messages():
    global messages
    if not messages:
        print("No messages to post.")
        return

    print("Posting messages...")
    for _ in range(min(10, len(messages))):  # Post up to 10 messages
        msg = messages.pop(0)
        try:
            await bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=msg)
        except Exception as e:
            print(f"Error in post_messages: {e}")
    print("Posted messages.")


async def main():
    await fetch_messages()
    await post_messages()

    scheduler.add_job(fetch_messages, 'interval', hours=24)
    scheduler.add_job(post_messages, 'interval', hours=24)
    scheduler.start()

    print("Bot is running...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
