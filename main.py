from time import localtime, sleep, strftime, time

import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from functions import *

import requests

angel_bot = telepot.Bot(
    '2043620030:AAGuHQQuWoejoeZy1MoRW6RUx9p_a4w7pdI')  # TOKEN HERE
mortal_bot = telepot.Bot(
    '1922226969:AAHDdp0oQFpHRgg-QHAlS7XYN3pw7xBhncg')


def on_chat(msg, bot, receiver_bot, receiver):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print("CHAT_ID", chat_id)
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
            # '/a': send_to(ANGEL),
            # '/angel': send_to(ANGEL),
            # '/m': send_to(MORTAL),
            # '/mortal': send_to(MORTAL),
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
                receiver_bot, chat_id, msg, message, content_type)
            print(response)
        # except KeyError:
        #     bot.sendMessage(
        #         chat_id, 'Invalid command! Please try again or type /help for help.')
        # bot.sendMessage(chat_id, 'Hello World!')
    elif content_type == 'photo':
        # try:
        message = msg.get('caption', "")
        # except KeyError:
        #     bot.sendMessage(chat_id, 'Please indicate whether you want to send your message to your angel or mortal in the caption.',
        #                     reply_to_message_id=msg['message_id'])
        print(f'{now} | Received a photo from {msg["from"]["username"]}')
        # command = message.split()[0]
        # message_text = message[(len(command)+1):]
        # command_handler = {
        #     '/a': send_to(ANGEL),
        #     '/angel': send_to(ANGEL),
        #     '/m': send_to(MORTAL),
        #     '/mortal': send_to(MORTAL),
        # }

        response = send_to(receiver)(
            receiver_bot, chat_id, msg, message, content_type)
        print(response)
        # try:
        #     ret = command_handler[command](
        #         bot, chat_id, msg, message_text, is_photo=True)
        #     if ret is not None:
        #         bot.sendMessage(
        #             chat_id, ret, reply_to_message_id=msg['message_id'])
        # except KeyError:
        #     bot.sendMessage(
        #         chat_id, 'Invalid command! Please indicate whether you want to send your message to your angel or mortal in the caption.')
    elif content_type == 'sticker':
        print(f'{now} | Received a sticker from {msg["from"]["username"]}')
        # file_id = msg['sticker']['file_id']
        # print(file_id)
        # bot.sendMessage(chat_id, 'Who do you want to send this sticker to?', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        #     [InlineKeyboardButton(text="Angel", callback_data='angel'), InlineKeyboardButton(
        #         text="Mortal", callback_data='mortal'), ],
        # ]), reply_to_message_id=msg['message_id'])
        response = send_to(receiver)(
            receiver_bot, chat_id, msg, "", content_type)
        print(response)
    else:
        bot.sendMessage(chat_id, build_invalid_content_type_message(
            content_type), reply_to_message_id=msg['message_id'])


# def on_callback_query(callback, bot):
#     callback_dict = {
#         'angel': send_sticker_to_angel,
#         'mortal': send_sticker_to_mortal,
#     }
#     origin = telepot.origin_identifier(callback)
#     ret = callback_dict[callback['data']](bot, callback['message'])
#     bot.editMessageReplyMarkup(origin, reply_markup=None)
#     bot.sendMessage(callback['message']['chat']['id'], ret,
#                     reply_to_message_id=callback['message']['reply_to_message']['message_id'])


angel_bot.message_loop({'chat': lambda msg: on_chat(
    msg, angel_bot, mortal_bot, MORTAL)})
mortal_bot.message_loop({'chat': lambda msg: on_chat(
    msg, mortal_bot, angel_bot, ANGEL)})

while True:
    sleep(10)
