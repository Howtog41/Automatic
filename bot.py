import asyncio
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '-1001984768732'
DESTINATION_CHANNEL_ID = '-1002115327472'

bot = Bot(token=API_TOKEN)
scheduler = AsyncIOScheduler()

# Messages store karne ke liye list
messages = []

# Function to fetch messages from the source channel
async def fetch_messages():
    global messages
    print("Fetching messages...")
    try:
        updates = await bot.get_updates()  # Fetch updates asynchronously
        for update in updates:
            if update.message and update.message.chat and update.message.chat.username == SOURCE_CHANNEL_ID.strip('@'):
                messages.append(update.message.text)
        print(f"Fetched {len(messages)} messages.")
    except Exception as e:
        print(f"Error in fetch_messages: {e}")

# Function to post messages to the destination channel
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
    # Fetch messages once at the start
    await fetch_messages()
    await post_messages()

    # Scheduler for regular operations
    scheduler.add_job(fetch_messages, 'interval', hours=24)  # Fetch every 24 hours
    scheduler.add_job(post_messages, 'interval', hours=24)   # Post every 24 hours
    scheduler.start()

    # Keep the script running
    print("Bot is running...")
    await asyncio.Event().wait()

# Start the asyncio loop
if __name__ == "__main__":
    asyncio.run(main())
