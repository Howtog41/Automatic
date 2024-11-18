import asyncio
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '-1001984768732'
DESTINATION_CHANNEL_ID = '-1002115327472'

messages = []  # Global list for storing messages
scheduler = AsyncIOScheduler()


async def fetch_messages(application: Application):
    global messages
    print("Fetching messages...")
    try:
        # Get messages from the source channel
        async for message in application.bot.get_chat_history(chat_id=SOURCE_CHANNEL_ID, limit=100):
            if message.text:
                messages.append(message.text)
        print(f"Fetched {len(messages)} messages.")
    except Exception as e:
        print(f"Error in fetch_messages: {e}")


async def post_messages(application: Application):
    global messages
    if not messages:
        print("No messages to post.")
        return

    print("Posting messages...")
    for _ in range(min(10, len(messages))):  # Post up to 10 messages
        msg = messages.pop(0)
        try:
            await application.bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=msg)
        except Exception as e:
            print(f"Error in post_messages: {e}")
    print("Posted messages.")


async def start_bot():
    print("Bot started...")

    # Fetch messages initially
    await fetch_messages()

    # Schedule periodic fetch and post tasks
    scheduler.add_job(fetch_messages, 'interval', hours=24, args=[app])
    scheduler.add_job(post_messages, 'interval', hours=24, args=[app])
    scheduler.start()


if __name__ == "__main__":
    # Initialize application
    app = Application.builder().token(API_TOKEN).build()

    # Run bot tasks
    app.run_task(start_bot())
    app.run_polling()
