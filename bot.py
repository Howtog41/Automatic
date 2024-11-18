from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ"
SOURCE_CHANNEL_ID = "@Old_Bollywood_movie_HD"  # Replace with source channel username or ID
DESTINATION_CHANNEL_ID = "@LKD_Latest_Korean_Dramaa"  # Replace with destination channel username or ID

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:  # Ensure it is a message from a channel
        await context.bot.forward_message(
            chat_id=DESTINATION_CHANNEL_ID,
            from_chat_id=update.channel_post.chat_id,
            message_id=update.channel_post.message_id,
        )
        print(f"Forwarded message: {update.channel_post.text}")

def main():
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handler for channel posts
    app.add_handler(MessageHandler(filters.ChannelUpdate.CHAT_POSTS, forward_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
