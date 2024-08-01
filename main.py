import telebot
import sqlite3
from threading import Timer
from utils import password_generator
from configs import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

db_connection = sqlite3.connect('manager.db')
cursor = db_connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS password(id integer, bookmark text not null, password text not null, username text, email text, url text, expiration text)')
cursor.close()


@bot.message_handler(commands=['start'])
def wellcome_message(message):
    text = "Wellcome to *Bot Generate Password Manager*"
    text += "\nPlease enable auto delete chat for this bot"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['generate'])
def handler_generate(message):
    text = "What length of password do you want?"
    print(f"{message.chat.id} request generating password...")
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, execute_generate)



@bot.message_handler(commands=['get'])
def handler_get_password(message):
    params = message.text.replace('/get ', '')
    print(f"params: {params}+")
    with sqlite3.connect('manager.db') as connection:
        c = connection.cursor()
        rows = c.execute('SELECT password FROM password WHERE bookmark = ?', (params,)).fetchone()
        if len(rows) > 0:
            bot.send_message(message.chat.id, rows)
        c.close()


@bot.message_handler(commands=['set'])
def handler_set(message):
    text = "Enter your password"
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, bookmark_set)


def bookmark_set(message):
    text = "Enter your bookmark"
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, password_set, message.text)


def password_set(message, password):
    text = f"Your password has been successfully saved with the *{message.text}* bookmark."
    print(f"/set_pass: Successfully set password for {message.chat.first_name}")
    with sqlite3.connect('manager.db') as connection:
        c = connection.cursor()
        c.execute('INSERT INTO password (id, bookmark, password) VALUES (?, ?, ?)',
                  (message.date, message.text, password))
        c.close()
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


def execute_generate(message):
    digit = message.text
    if digit.isnumeric():
        password = password_generator(int(digit))
        text = f"{password}\n\nEnter your bookmark if you want to save your password\n\nThis chat automatic deleted after 30 seconds"
        if password:
            print("Password generated")
        send_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(send_msg, save_generate, password, send_msg.message_id)
        auto_delete = Timer(30, delete_generate, (message.chat.id, send_msg.message_id))
        auto_delete.start()
    else:
        send_msg = bot.send_message(message.chat.id, "Please enter a digit")
        bot.register_next_step_handler(send_msg, execute_generate)


def delete_generate(chat_id, message_id):
    print(f"Password chat deleted {message_id}")
    bot.delete_message(chat_id, message_id)
    bot.clear_step_handler_by_chat_id(chat_id)


def save_generate(message, password, message_id):
    text = f"Your password has been successfully saved with the *{message.text}* bookmark."
    print(f"Processing save data password {message_id}")
    with sqlite3.connect('manager.db') as connection:
        c = connection.cursor()
        c.execute('INSERT INTO password (id, bookmark, password) VALUES (?, ?, ?)',
                   (message.date, message.text, password))
        c.close()
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


if __name__ == '__main__':
    bot.infinity_polling()
    bot.delete_webhook()
