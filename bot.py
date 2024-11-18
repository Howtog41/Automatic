import asyncio
from telegram.ext import Application, ContextTypes
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '-1001984768732'
DESTINATION_CHANNEL_ID = '-1002115327472'

scheduler = AsyncIOScheduler()
messages = []

# Function to fetch message history
async def fetch_messages(application: Application):
    global messages
    print("Fetching messages...")
    try:
        async with application.bot:
            async for message in application.bot.get_chat_history(chat_id=SOURCE_CHANNEL_ID, limit=50):  # Fetch last 50 messages
                if message.text:  # Only consider text messages
                    messages.append(message.text)
        print(f"Fetched {len(messages)} messages.")
    except Exception as e:
        print(f"Error in fetch_messages: {e}")

# Function to post messages to destination channel
async def post_messages(application: Application):
    global messages
    if len(messages) >= 10:
        print("Posting messages...")
        for _ in range(10):
            msg = messages.pop(0)
            try:
                await application.bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=msg)
            except Exception as e:
                print(f"Error in post_messages: {e}")
        print("Posted 10 messages.")

# Main function to run the bot
async def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    # Fetch and post messages immediately
    await fetch_messages(app)
    await post_messages(app)

    # Schedule jobs for daily operations
    scheduler.add_job(fetch_messages, 'interval', hours=24, args=(app,))
    scheduler.add_job(post_messages, 'interval', hours=24, args=(app,))
    scheduler.start()

    print("Bot is running...")
    await asyncio.Event().wait()

# Run the asyncio loop
if __name__ == "__main__":
    asyncio.run(main())
