import schedule
import time
from pyrogram import Client
from datetime import datetime
import random  # For generating different messages

# Set up your bot (in config.py)
app = Client("my_bot", api_id="15502786", api_hash="bb32e00647b1bfe66e6cd298a2c66a5a", bot_token="5725026746:AAES6vUC808RmEhh6_ZAZxwGeu603nZEAt4")

# Function to send message
def send_scheduled_message():
    with app:
        # Load the message to be sent (random message from a list)
        messages = ["Hello World!", "This is a daily post!", "Have a nice day!"]
        message = random.choice(messages)
        
        # Send message to a specific channel
        app.send_message(chat_id="CHANNEL_ID", text=message)

# Function to schedule the posts
def schedule_daily_post(time_of_post="23:02", post_count=3):
    # Schedule the post at the specified time
    schedule.every().day.at(time_of_post).do(send_scheduled_message)
    
    for _ in range(post_count - 1):
        # Additional messages if post_count is more than 1
        schedule.every().day.at(time_of_post).do(send_scheduled_message)

# Start the schedule
def run_bot():
    schedule_daily_post(time_of_post="23:02", post_count=3)  # Set your time and post count here
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_bot()
