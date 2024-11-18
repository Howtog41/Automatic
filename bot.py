import asyncio
from telegram.ext import Application, ContextTypes
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '-1001984768732'
DESTINATION_CHANNEL_ID = '-1002115327472'


messages = []  # Global list to store messages
scheduler = AsyncIOScheduler()


async def fetch_messages(application: Application):
    global messages
    print("Fetching messages...")
    try:
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


async def start_scheduler(application: Application):
    # Schedule periodic tasks
    scheduler.add_job(fetch_messages, 'interval', hours=24, args=[application])
    scheduler.add_job(post_messages, 'interval', hours=24, args=[application])
    scheduler.start()


async def main():
    # Create the bot application
    application = Application.builder().token(API_TOKEN).build()

    # Fetch messages initially and start the scheduler
    await fetch_messages(application)
    await start_scheduler(application)

    # Start polling to keep the bot running
    print("Bot is running...")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
