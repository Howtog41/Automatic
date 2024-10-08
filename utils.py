# utils.py
from telegram import Update

async def extract_channel_id_from_message(update: Update):
    if update.message.forward_from_chat:
        return update.message.forward_from_chat.id
    return None

def validate_channel_id(channel_id):
    return isinstance(channel_id, int)
