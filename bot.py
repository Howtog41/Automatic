import asyncio
from telegram.ext import Application, ContextTypes
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '-1001984768732'
DESTINATION_CHANNEL_ID = '-1002115327472'

bot = Bot(token=API_TOKEN)
scheduler = AsyncIOScheduler()

messages = []

# Function to fetch message history
async def fetch_messages():
    global messages
    print("Fetching messages...")
    try:
        async for message in bot.get_chat(chat_id=SOURCE_CHANNEL_ID): # Fetch last 50 messages
            if message.text:  # Only consider text messages
                messages.append(message.text)
        print(f"Fetched {len(messages)} messages.")
    except Exception as e:
        print(f"Error in fetch_messages: {e}")

# Function to post messages to destination channel
async def post_messages():
    global messages
    if len(messages) >= 10:
        print("Posting messages...")
        for _ in range(10):
            msg = messages.pop(0)
            try:
                await bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=msg)
            except Exception as e:
                print(f"Error in post_messages: {e}")
        print("Posted 10 messages.")

# Main function to initialize and run the bot
async def main():
    await fetch_messages()
    await post_messages()

    scheduler.add_job(fetch_messages, 'interval', hours=24)
    scheduler.add_job(post_messages, 'interval', hours=24)
    scheduler.start()

    print("Bot is running...")
    await asyncio.Event().wait()

# Run the asyncio loop
if __name__ == "__main__":
    asyncio.run(main())
