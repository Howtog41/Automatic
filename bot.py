import telebot
import time

# अपना API टोकन यहां डालें
bot = telebot.TeleBot("-10019847687325645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ")

# जिस चैनल से मैसेज लेने हैं उसका ID
source_chat_id = "@Old_Bollywood_movie_HD" # उदाहरण के लिए

# जिस चैनल पर मैसेज पोस्ट करने हैं उसका ID
destination_chat_id = "@LKD_Latest_Korean_Dramaa" # उदाहरण के लिए

def send_messages():
    messages = bot.get_chat_history(chat_id=source_chat_id)
    for message in messages[:10]:
        bot.send_message(chat_id=destination_chat_id, text=message.text)

while True:
    send_messages()
    time.sleep(86400)  # हर 24 घंटे में एक बार चलाएगा

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
