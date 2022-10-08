from time import localtime, sleep, strftime, time

import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from functions import *

import os
from dotenv import load_dotenv

load_dotenv()
angel_bot = telepot.Bot(
    os.environ.get('ANGEL_BOT_TOKEN')) 
mortal_bot = telepot.Bot(
    os.environ.get('MORTAL_BOT_TOKEN'))

# receiver_bot = bot that receives message from user
# sender_bot = bot that sends the received message; always different from receiver_bot
# receiver = user that receives the message from sender_bot; either angel or mortal
def on_chat(msg, receiver_bot, sender_bot, receiver):
    content_type, chat_type, chat_id = telepot.glance(msg)

    # for messages from files channel
    if chat_type == 'channel' and msg['chat']['id'] == int(os.environ.get('FILES_CHANNEL_ID')):
        return send_file_from_channel(msg, receiver_bot, sender_bot, receiver)

    # now = time.strftime('%A, %Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    now = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    print(f'{now} | Received a message from {msg["from"]["username"]}')
    
    if content_type == 'text':
        message = msg['text']
        command = message.split()[0]
        message_text = message[(len(command)+1):]
        # command, message_text = message.split(maxsplit=1) # doesn't work when message == command only
        
        # args for start: receiver_bot, sender_bot, chat_id, msg, message_text, receiver
        # args for startgame: receiver_bot, mortal_bot, angel_bot, chat_id, msg, message_text
        # args for other commands: receiver_bot, sender_bot, chat_id, msg, message_text
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
            # '/assign': assign_pairings,
        }
        # try:
        func = command_handler.get(command, None)
        if func is not None:        # check if message invokes a commnad
            response = ''
            if command == '/startgame' and receiver == ANGEL:   # then receiver_bot == angel_bot, sender_bot == mortal_bot
                response = func(receiver_bot, sender_bot, receiver_bot, chat_id, msg, message_text)
            elif command == '/startgame' and receiver == MORTAL:    # then receiver_bot == mortal_bot, sender_bot == angel_bot
                response = func(receiver_bot, receiver_bot, sender_bot, chat_id, msg, message_text)
            elif command == '/start':
                response = func(receiver_bot, sender_bot, chat_id, msg, message_text, receiver)
            else:
                response = func(receiver_bot, sender_bot, chat_id, msg, message_text)
            
            if response:
                receiver_bot.sendMessage(chat_id, response,
                                reply_to_message_id=msg['message_id'])
        else:                       # message is just plain text to be sent to the other bot
            response = send_to(receiver)(
                receiver_bot, sender_bot, chat_id, msg, message, content_type)
            print(response)
    else:       # message is a file (e.g. sticker, video note)
        message = msg.get('caption', "")
        response = send_to(receiver)(
            receiver_bot, sender_bot, chat_id, msg, message, content_type)
        print(response)

angel_bot.message_loop({'chat': lambda msg: on_chat(
    msg, angel_bot, mortal_bot, ANGEL)})
mortal_bot.message_loop({'chat': lambda msg: on_chat(
    msg, mortal_bot, angel_bot, MORTAL)})

while True:
    sleep(10)
