import pytz
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Variables
SOURCE_CHANNEL = None
TARGET_CHANNEL = None
MESSAGE_COUNT = None
FORWARD_TIME = None
USER_TIMEZONE = None
scheduler = BackgroundScheduler()

# Timezones
SERVER_TZ = pytz.timezone('UTC')  # Set this to the server's timezone, e.g., UTC
LOCAL_TZ = pytz.timezone('Asia/Kolkata')  # Set this to your local timezone

# Conversation states
SET_SOURCE_CHANNEL, SET_TARGET_CHANNEL, SET_COUNT, SET_TIME, SET_TIMEZONE = range(5)

# Command /start
async def start(update: Update, context):
    await update.message.reply_text("Welcome to the Telegram Forward Bot! Use /set_channel to begin.")

# Command /set_channel
async def set_channel(update: Update, context):
    await update.message.reply_text("Please send the source channel ID or username (starting with @).")
    return SET_SOURCE_CHANNEL

# Command /set_message_count
async def set_message_count(update: Update, context):
    await update.message.reply_text("How many messages would you like to forward daily?")
    return SET_COUNT

# Command /set_time
async def set_time(update: Update, context):
    await update.message.reply_text("Please set the time for forwarding messages in HH:MM (24-hour format) in your local time zone.")
    return SET_TIME

# Command /set_timezone
async def set_timezone(update: Update, context):
    await update.message.reply_text("Please send your local timezone (e.g., 'Asia/Kolkata', 'America/New_York').")
    return SET_TIMEZONE

# Handler for SET_SOURCE_CHANNEL
async def source_channel_handler(update: Update, context):
    global SOURCE_CHANNEL
    SOURCE_CHANNEL = update.message.text
    await update.message.reply_text(f"Source channel set to: {SOURCE_CHANNEL}. Now, send the target channel ID or username (starting with @).")
    return SET_TARGET_CHANNEL

# Handler for SET_TARGET_CHANNEL
async def target_channel_handler(update: Update, context):
    global TARGET_CHANNEL
    TARGET_CHANNEL = update.message.text
    await update.message.reply_text(f"Target channel set to: {TARGET_CHANNEL}. Now, use /set_message_count to set the number of messages to forward.")
    return ConversationHandler.END

# Handler for message count
async def message_count_handler(update: Update, context):
    global MESSAGE_COUNT
    try:
        MESSAGE_COUNT = int(update.message.text)
        await update.message.reply_text(f"Message count set to {MESSAGE_COUNT}. Now, use /set_time to set the forwarding time.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please send a valid number for message count.")
        return SET_COUNT

# Handler for time setting
async def time_handler(update: Update, context):
    global FORWARD_TIME
    try:
        # Parse the user input time (local time)
        local_time_str = update.message.text  # Get the text that the user sent
        local_time = datetime.datetime.strptime(local_time_str, "%H:%M").time()  # Convert the string to time

        now = datetime.datetime.now(LOCAL_TZ)  # Get the current date and time in the user's timezone
        user_time = datetime.datetime.combine(now.date(), local_time)  # Combine current date with user time

        # Localize the user time to the user's timezone
        user_time = LOCAL_TZ.localize(user_time)

        # Convert the user time to server timezone
        server_time = user_time.astimezone(SERVER_TZ)
        FORWARD_TIME = server_time.time()  # Store the time in server timezone

        await update.message.reply_text(f"Forward time set to {FORWARD_TIME} in server time ({SERVER_TZ}).")
        return ConversationHandler.END
    except ValueError:
        # If time format is wrong
        await update.message.reply_text("Invalid time format. Please send the time in HH:MM format.")
        return SET_TIME

# Handler for timezone setting
async def timezone_handler(update: Update, context):
    global LOCAL_TZ
    try:
        USER_TIMEZONE = update.message.text
        LOCAL_TZ = pytz.timezone(USER_TIMEZONE)
        await update.message.reply_text(f"Timezone set to {USER_TIMEZONE}. Now, use /set_time to set the forwarding time.")
        return ConversationHandler.END
    except Exception:
        await update.message.reply_text("Invalid timezone. Please enter a valid timezone.")
        return SET_TIMEZONE

# Forward messages function
async def forward_messages(context):
    job = context.job
    bot = context.bot
    try:
        # Forward the latest `MESSAGE_COUNT` messages from source to target
        messages = await bot.get_chat(SOURCE_CHANNEL).history(limit=MESSAGE_COUNT)
        for message in messages:
            await bot.forward_message(chat_id=TARGET_CHANNEL, from_chat_id=SOURCE_CHANNEL, message_id=message.message_id)
        logger.info(f"Forwarded {MESSAGE_COUNT} messages from {SOURCE_CHANNEL} to {TARGET_CHANNEL}.")
    except Exception as e:
        logger.error(f"Error forwarding messages: {e}")

# Start forwarding
async def start_forwarding(update: Update, context):
    if SOURCE_CHANNEL and TARGET_CHANNEL and MESSAGE_COUNT and FORWARD_TIME:
        # Schedule the message forwarding at the set time every day
        scheduler.add_job(forward_messages, 'cron', hour=FORWARD_TIME.hour, minute=FORWARD_TIME.minute, args=[context])
        scheduler.start()
        await update.message.reply_text(f"Forwarding scheduled at {FORWARD_TIME} daily in server time ({SERVER_TZ}).")
    else:
        await update.message.reply_text("Please make sure to set the source channel, target channel, message count, and time first.")

# Stop forwarding
async def stop_forwarding(update: Update, context):
    scheduler.remove_all_jobs()
    await update.message.reply_text("Forwarding has been stopped.")

# Error handler
async def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    application = ApplicationBuilder().token('5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4').build()

    # Handlers for conversation states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set_channel', set_channel)],
        states={
            SET_SOURCE_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, source_channel_handler)],
            SET_TARGET_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, target_channel_handler)],
            SET_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_count_handler)],
            SET_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_handler)],
            SET_TIMEZONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, timezone_handler)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('set_message_count', set_message_count))
    application.add_handler(CommandHandler('set_time', set_time))
    application.add_handler(CommandHandler('set_timezone', set_timezone))
    application.add_handler(CommandHandler('start_forwarding', start_forwarding))
    application.add_handler(CommandHandler('stop_forwarding', stop_forwarding))
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling()
