import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables to store user settings
SOURCE_CHANNEL = None
TARGET_CHANNEL = None
MESSAGE_COUNT = None
FORWARD_TIME = None

# Conversation states
SET_CHANNEL, SET_TARGET_CHANNEL, SET_MESSAGE_COUNT, SET_TIME = range(4)

# Command to start the bot
async def start(update: Update, context):
    await update.message.reply_text("Welcome to the Telegram Forward Bot! Use /set_channel to begin.")

# Handler to set the source channel
async def set_channel(update: Update, context):
    await update.message.reply_text("Please send the source channel ID or username (starting with @).")
    return SET_CHANNEL

# Handler to process the source channel input
async def source_channel_handler(update: Update, context):
    global SOURCE_CHANNEL
    SOURCE_CHANNEL = update.message.text
    await update.message.reply_text(f"Source channel set to: {SOURCE_CHANNEL}. Now, send the target channel ID or username (starting with @).")
    return SET_TARGET_CHANNEL

# Handler to process the target channel input
async def target_channel_handler(update: Update, context):
    global TARGET_CHANNEL
    TARGET_CHANNEL = update.message.text
    await update.message.reply_text(f"Target channel set to: {TARGET_CHANNEL}. Now, use /set_message_count to set the number of messages to forward.")
    return ConversationHandler.END

# Command to set message count
async def set_message_count(update: Update, context):
    await update.message.reply_text("How many messages would you like to forward daily?")
    return SET_MESSAGE_COUNT

# Handler to process message count input
async def message_count_handler(update: Update, context):
    global MESSAGE_COUNT
    try:
        MESSAGE_COUNT = int(update.message.text)
        await update.message.reply_text(f"Message count set to {MESSAGE_COUNT}. Now set the time using /set_time.")
        return SET_TIME
    except ValueError:
        await update.message.reply_text("Please send a valid number for message count.")
        return SET_MESSAGE_COUNT

# Command to set time
async def set_time(update: Update, context):
    await update.message.reply_text("Please set the time for forwarding messages in HH:MM (24-hour format) in your local time zone.")
    return SET_TIME

# Handler to process time input
async def time_handler(update: Update, context):
    global FORWARD_TIME
    FORWARD_TIME = update.message.text
    try:
        # Validate the time format (HH:MM)
        hours, minutes = map(int, FORWARD_TIME.split(":"))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            await update.message.reply_text(f"Forwarding time set to {FORWARD_TIME}. Use /start_forwarding to begin.")
            return ConversationHandler.END
        else:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid time format. Please enter the time in HH:MM (24-hour format).")
        return SET_TIME

# Command to start the message forwarding process
async def start_forwarding(update: Update, context):
    global SOURCE_CHANNEL, TARGET_CHANNEL, MESSAGE_COUNT, FORWARD_TIME

    # Check if all required parameters are set
    if SOURCE_CHANNEL is None:
        await update.message.reply_text("Source channel not set. Please use /set_channel to set the source channel.")
        return
    if TARGET_CHANNEL is None:
        await update.message.reply_text("Target channel not set. Please use /set_channel to set the target channel.")
        return
    if MESSAGE_COUNT is None:
        await update.message.reply_text("Message count not set. Please use /set_message_count to set the number of messages.")
        return
    if FORWARD_TIME is None:
        await update.message.reply_text("Forwarding time not set. Please use /set_time to set the time for forwarding.")
        return

    await update.message.reply_text(f"Starting message forwarding from {SOURCE_CHANNEL} to {TARGET_CHANNEL} daily at {FORWARD_TIME}.")

    # Schedule message forwarding at the specified time
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour=int(FORWARD_TIME.split(":")[0]), minute=int(FORWARD_TIME.split(":")[1]))
    scheduler.add_job(forward_messages, trigger, args=[context.bot], id="forward_job", replace_existing=True)
    scheduler.start()

# Function to forward messages (dummy implementation)
async def forward_messages(bot):
    global SOURCE_CHANNEL, TARGET_CHANNEL, MESSAGE_COUNT
    # Add logic to forward the set number of messages from SOURCE_CHANNEL to TARGET_CHANNEL
    # Dummy response for now
    logger.info(f"Forwarding {MESSAGE_COUNT} messages from {SOURCE_CHANNEL} to {TARGET_CHANNEL}.")

# Main function to start the bot
def main():
    application = ApplicationBuilder().token("5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4").build()

    # Add command handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('set_channel', set_channel)],
        states={
            SET_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, source_channel_handler)],
            SET_TARGET_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, target_channel_handler)],
            SET_MESSAGE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_count_handler)],
            SET_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_handler)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("set_message_count", set_message_count))
    application.add_handler(CommandHandler("set_time", set_time))
    application.add_handler(CommandHandler("start_forwarding", start_forwarding))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
