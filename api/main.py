from flask import Flask, request

from time import localtime, sleep, strftime, time

import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from telepot.loop import OrderedWebhook

from functions import *

import os
from dotenv import load_dotenv

# receiver_bot = bot that receives message from user
# sender_bot = bot that sends the received message; always different from receiver_bot
# receiver = user that receives the message from sender_bot; either angel or mortal
def on_chat(msg, receiver_bot, sender_bot, receiver):
    content_type, chat_type, chat_id = telepot.glance(msg)

    # for files from files channel
    if chat_type == 'channel' and msg['chat']['id'] == int(os.environ.get('FILES_CHANNEL_ID')):
        to_be_printed = send_file_from_channel(msg, receiver_bot, sender_bot, receiver)
        print(to_be_printed)
        return

    now = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    print(f'{now} | Received a message from {msg["from"]["username"]}')
    
    if content_type == 'text':
        message = msg['text']
        command = message.split()[0]
        message_text = message[(len(command)+1):]
        
        # returns the corresponding function from functions.py for a command string
        command_handler = {
            '/register': register,
            '/verify': verify,
            '/checkreg': check_registration,
            '/startgame': start_game,
            '/reload': reload_players_data,
            '/start': start,
            '/help': help_me,
            '/update': update,
            '/reveal': reveal,
            '/announce': announce,
        }
        func = command_handler.get(command, None)

        # args for startgame: receiver_bot, mortal_bot, angel_bot, chat_id, msg, message_text
        # args for start: receiver_bot, sender_bot, chat_id, msg, message_text, receiver
        # args for other commands: receiver_bot, sender_bot, chat_id, msg, message_text
        if func is not None:        # check if message invokes a commnad
            reply_message = ''
            if command == '/startgame' and receiver == ANGEL:   # then receiver_bot is angel bot, sender_bot is mortal bot
                reply_message = func(receiver_bot, sender_bot, receiver_bot, chat_id, msg, message_text)
            elif command == '/startgame' and receiver == MORTAL:    # then receiver_bot is mortal bot, sender_bot is angel bot
                reply_message = func(receiver_bot, receiver_bot, sender_bot, chat_id, msg, message_text)
            elif command == '/start':
                reply_message = func(receiver_bot, sender_bot, chat_id, msg, message_text, receiver)
            else:
                reply_message = func(receiver_bot, sender_bot, chat_id, msg, message_text)
            
            if reply_message:
                receiver_bot.sendMessage(chat_id, reply_message,
                                reply_to_message_id=msg['message_id'])
        else:                       # message is just plain text to be sent to the other bot
            to_be_printed = send_to_person(
                receiver, receiver_bot, sender_bot, chat_id, msg, message, content_type)
            print(to_be_printed)
    else:       # message is a file (e.g. sticker, video note)
        message = msg.get('caption', "")
        to_be_printed = send_to_person(
            receiver, receiver_bot, sender_bot, chat_id, msg, message, content_type)
        print(to_be_printed)

load_dotenv()
angel_bot = telepot.Bot(
    os.environ.get('ANGEL_BOT_TOKEN')) 
mortal_bot = telepot.Bot(
    os.environ.get('MORTAL_BOT_TOKEN'))

angel_bot_webhook = OrderedWebhook(angel_bot, {
    'chat': lambda msg: on_chat(
    msg, angel_bot, mortal_bot, ANGEL)
})
mortal_bot_webhook = OrderedWebhook(mortal_bot, {
    'chat': lambda msg: on_chat(
    msg, mortal_bot, angel_bot, ANGEL)
})

app = Flask(__name__)

@app.route('/angel', methods=['POST'])
def process_angel_bot_received_messages():
    angel_bot_webhook.feed(request.data)
    return 'OK'

@app.route('/mortal', methods=['POST'])
def process_mortal_bot_received_messages():
    mortal_bot_webhook.feed(request.data)
    return 'OK'

if '__name__' == '__main__':
    angel_bot.setWebhook(os.environ.get('VERCEL_URL') + '/angel')
    mortal_bot.setWebhook(os.environ.get('VERCEL_URL') + '/mortal')

    angel_bot_webhook.run_as_thread()
    mortal_bot_webhook.run_as_thread()

    app.run(port = os.environ.get('PORT'))