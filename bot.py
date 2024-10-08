# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from forwarding import ForwardingTask
from utils import extract_channel_id_from_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# A dictionary to store forwarding instructions
forward_instructions = {}

async def start(update: Update, context):
    await update.message.reply_text("Welcome! Use /setforward to set a forwarding task.")

async def setforward(update: Update, context):
    context.user_data['step'] = 'source_channel'
    await update.message.reply_text("Please forward a message from the source channel.")

async def handle_forward_message(update: Update, context):
    step = context.user_data.get('step')

    if step == 'source_channel':
        source_channel_id = await extract_channel_id_from_message(update)
        if source_channel_id:
            context.user_data['source_channel'] = source_channel_id
            context.user_data['step'] = 'destination_channel'
            await update.message.reply_text("Source channel set. Now forward a message from the destination channel.")
        else:
            await update.message.reply_text("Failed to extract source channel ID. Please try again.")
    
    elif step == 'destination_channel':
        destination_channel_id = await extract_channel_id_from_message(update)
        if destination_channel_id:
            context.user_data['destination_channel'] = destination_channel_id
            context.user_data['step'] = 'message_limit'
            await update.message.reply_text("Destination channel set. Please enter the message limit.")
        else:
            await update.message.reply_text("Failed to extract destination channel ID. Please try again.")

async def handle_message_limit(update: Update, context):
    message_limit = int(update.message.text)
    context.user_data['message_limit'] = message_limit
    context.user_data['step'] = 'delay'
    await update.message.reply_text(f"Message limit set to {message_limit}. Now enter the time delay in hours.")

async def handle_delay(update: Update, context):
    delay = int(update.message.text)
    source_channel = context.user_data.get('source_channel')
    destination_channel = context.user_data.get('destination_channel')
    message_limit = context.user_data.get('message_limit')

    # Save the forwarding task
    task = ForwardingTask(source_channel, destination_channel, message_limit, delay)
    forward_instructions[update.effective_chat.id] = task
    await update.message.reply_text(f"Forward task created! Messages will be forwarded every {delay} hours.")

async def view_forward_tasks(update: Update, context):
    keyboard = []

    for task_id, task in forward_instructions.items():
        keyboard.append([InlineKeyboardButton(f"Task {task_id}", callback_data=str(task_id))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here are your forwarding tasks:", reply_markup=reply_markup)

async def handle_task_selection(update: Update, context):
    query = update.callback_query
    task_id = int(query.data)

    task = forward_instructions.get(task_id)
    if task:
        buttons = [
            InlineKeyboardButton("Activate", callback_data=f"activate_{task_id}"),
            InlineKeyboardButton("Deactivate", callback_data=f"deactivate_{task_id}"),
            InlineKeyboardButton("Delete", callback_data=f"delete_{task_id}")
        ]
        reply_markup = InlineKeyboardMarkup([buttons])

        await query.message.reply_text(f"Task {task_id}:\nSource: {task.source_channel}\nDestination: {task.destination_channel}\nMessage Limit: {task.message_limit}\nDelay: {task.delay} hours")
        await query.message.reply_text("Choose an action:", reply_markup=reply_markup)

async def handle_task_action(update: Update, context):
    query = update.callback_query
    action, task_id = query.data.split("_")
    task_id = int(task_id)

    if task_id in forward_instructions:
        if action == "activate":
            forward_instructions[task_id].activate()
            await query.message.reply_text(f"Task {task_id} activated.")
        elif action == "deactivate":
            forward_instructions[task_id].deactivate()
            await query.message.reply_text(f"Task {task_id} deactivated.")
        elif action == "delete":
            del forward_instructions[task_id]
            await query.message.reply_text(f"Task {task_id} deleted.")
        else:
            await query.message.reply_text("Invalid action.")

async def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('setforward', setforward))
    application.add_handler(CommandHandler('view', view_forward_tasks))
    application.add_handler(MessageHandler(filters.FORWARDED, handle_forward_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_limit))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delay))
    application.add_handler(CallbackQueryHandler(handle_task_selection))
    application.add_handler(CallbackQueryHandler(handle_task_action))

    # Initialize the application
    await application.initialize()  # <--- This is the missing initialization step

    # Start the Bot
    await application.start()
    await application.wait_for_shutdown()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
