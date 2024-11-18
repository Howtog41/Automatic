from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

API_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'
SOURCE_CHANNEL_ID = '@Old_Bollywood_movie_HD'
DESTINATION_CHANNEL_ID = '@LKD_Latest_Korean_Dramaa'

bot = Bot(token=API_TOKEN)
scheduler = AsyncIOScheduler()

# Messages store karne ke liye list
messages = []

# Function: Messages fetch karna
async def fetch_messages():
    global messages
    updates = await bot.get_updates()
    for update in updates:
        if update.message and update.message.chat.username == 'source_channel':
            messages.append(update.message.text)

# Function: Messages post karna
async def post_messages():
    global messages
    if len(messages) >= 10:
        for _ in range(10):
            msg = messages.pop(0)
            try:
                await bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=msg)
            except Exception as e:
                print(f"Error: {e}")

# Main function to run everything
async def main():
    await fetch_messages()  # Turant messages fetch karein
    await post_messages()   # Turant messages post karein

    # Scheduler setup
    scheduler.add_job(fetch_messages, 'interval', hours=24)
    scheduler.add_job(post_messages, 'interval', hours=24)
    scheduler.start()

    # Keep script running
    await asyncio.Event().wait()

# Run the main function
asyncio.run(main())
