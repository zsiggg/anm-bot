from time import localtime, sleep, strftime, time

import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from functions import *

import os
from dotenv import load_dotenv

load_dotenv()
angel_bot = telepot.Bot(
    os.environ.get('ANGEL_BOT_TOKEN'))  # TOKEN HERE
mortal_bot = telepot.Bot(
    os.environ.get('MORTAL_BOT_TOKEN'))


def on_chat(msg, bot, receiver_bot, receiver):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # now = time.strftime('%A, %Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    now = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    # now = ctime(time())
    if content_type == 'text':
        message = msg['text']
        print(f'{now} | Received a message from {msg["from"]["username"]}')
        command = message.split()[0]
        message_text = message[(len(command)+1):]
        # command, message_text = message.split(maxsplit=1) # doesn't work when message == command only
        command_handler = {
            '/register': register,
            '/verify': verify,
            '/checkreg': check_registration,
            '/startgame': start_game,
            '/reload': reload_players_data,
            '/start': start,
            '/help': help_me,
            '/update': update_username,
            '/reveal': reveal,
            '/announce': announce,
            # '/assign': assign_pairings,
        }
        # try:
        func = command_handler.get(command, None)
        if func is not None:        # check if message invokes a commnad
            response = func(bot, chat_id, msg, message_text)
            if response:
                bot.sendMessage(chat_id, response,
                                reply_to_message_id=msg['message_id'])
        else:                       # message is just plain text to be sent to the other bot
            response = send_to(receiver)(
                receiver_bot, bot, chat_id, msg, message, content_type)
            print(response)
    else:
        message = msg.get('caption', "")
        response = send_to(receiver)(
            receiver_bot, bot, chat_id, msg, message, content_type)
        print(response)
    # elif content_type == 'photo':
    #     message = msg.get('caption', "")
    #     print(f'{now} | Received a photo from {msg["from"]["username"]}')
    #     response = send_to(receiver)(
    #         receiver_bot, bot, chat_id, msg, message, content_type)
    #     print(response)
    # elif content_type in ['sticker', 'video_note']:     # no caption content_type
    #     print(f'{now} | Received a sticker from {msg["from"]["username"]}')
    #     response = send_to(receiver)(
    #         receiver_bot, bot, chat_id, msg, "", content_type)   # pass in empty message_text
    #     print(response)
    # else:
    #     bot.sendMessage(chat_id, build_invalid_content_type_message(
    #         content_type), reply_to_message_id=msg['message_id'])


angel_bot.message_loop({'chat': lambda msg: on_chat(
    msg, angel_bot, mortal_bot, MORTAL)})
mortal_bot.message_loop({'chat': lambda msg: on_chat(
    msg, mortal_bot, angel_bot, ANGEL)})

while True:
    sleep(10)
