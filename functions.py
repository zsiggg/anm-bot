import csv
import pickle
from random import randint, shuffle

import numpy as np

from constants import *


class Player():
    def __init__(self, name, username, diet_pref, favourites, note_for_angel, fun_fact, open_to_pranks):
        self.number_of_starts = 0   # this will be incremented for every /start command run
        self.chat_id = None     # this will be set later on with update_chat_id
        self.name = name
        self.username = username
        self.diet_pref = diet_pref
        self.favourites = favourites
        self.note_for_angel = note_for_angel
        self.fun_fact = fun_fact
        self.open_to_pranks = open_to_pranks


    def update_chat_id(self, chat_id):
        self.chat_id = chat_id

    def update_username(self, username):
        self.username = username


# FOR TESTING
# groups = np.array([[Player('Zsigmond', 'zsiggg', 'M', 'test', 'N', <chat_id>), Player(
#     'Zsigmond', 'zsiggg', 'M', 'test gift', 'N', <chat_id>), ], ])

# FOR REAL USE
with open('players.pickle', 'rb') as f:
    groups = pickle.load(f)

with open('game_started.txt', 'r') as f:
    game_started = int(f.read())
# game_started = False


def update_players_database():      # writes groups into a pickle; called upon new data given
    global groups
    with open('players.pickle', 'wb') as f:
        pickle.dump(groups, f)


def announce(receiver_bot, sender_bot, chat_id, msg, message_text):      # sends a custom message all players
    message_text_split = message_text.split(maxsplit=1)
    if PASSWORD != message_text_split[0]:
        return 'Unauthorized.'
    for group in groups:
        for player in group:
            receiver_bot.sendMessage(
                player.chat_id, f'Hi {player.name}, House Comm has made a new ANNOUNCEMENT, see below:\n\n{message_text_split[1]}')
    return 'Your announcement has been broadcasted to everyone!'


# sends a message to all players revealing their own group numbers
def reveal(receiver_bot, sender_bot, chat_id, msg, message_text):
    if PASSWORD not in message_text:
        return 'Unauthorized.'
    for group_index, group in enumerate(groups):
        for player in group:
            receiver_bot.sendMessage(player.chat_id, f'<b>✨THE BIG REVEAL✨</b>\n\nHi {player.name}, thank you for participating in Rusa Angels and Mortals! As we bring this event to a close, we invite you to come to THE LAWN from 8-10pm TONIGHT 🎉\n\nAre you excited to find out who your angel is? Hint - you may find this group number helpful: <code>{group_index + 1}</code>\n\nSee you guys there! 👀💓', parse_mode='HTML')
    return 'Pairings revealed!'


def check_registration(receiver_bot, sender_bot, chat_id, msg, message_text):
    if PASSWORD not in message_text:
        return 'Unauthorized.'
    remaining = np.where(np.vectorize(lambda x: x.chat_id,
                         otypes=[Player])(groups) == None)
    length = len(list(zip(*remaining)))
    if length:
        names = np.vectorize(lambda x: x.name)(groups[remaining])
        shuffle(names)
        names = '\n'.join(names)
        return f'Not everyone has registered yet. Remaining {length} people out of {groups.size} total:\n\n{names}'
    return f'All {groups.size} people has registered with the bot. Safe to start game.'


def reload_players_data(receiver_bot, sender_bot, chat_id, msg, message_text):
    global groups
    if PASSWORD not in message_text:
        return 'Unauthorized.'
    groups = []
    with open('players.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            groups += [[Player(*(row[7*i:7*(i+1)]))
                        for i in range(GROUP_SIZE)]]
    groups = np.array(groups)
    update_players_database()
    return f'Players data successfully reloaded! {len(groups)} groups of {GROUP_SIZE} found.'


############################### SECTION: SEND TO PEOPLE ###############################

def get_angel_of(player_username):
    return groups[tuple((np.array(list(zip(*np.where(np.vectorize(lambda x: x.username.strip())(groups) == player_username)))[0]) - [0, 1]) % [len(groups), GROUP_SIZE])]


def get_mortal_of(player_username):
    return groups[tuple((np.array(list(zip(*np.where(np.vectorize(lambda x: x.username.strip())(groups) == player_username)))[0]) + [0, 1]) % [len(groups), GROUP_SIZE])]


def send_to(person):
    def send_to_person(receiver_bot, sender_bot, chat_id, msg, message_text, content_type):
        global game_started
        if not game_started:
            return GAME_NOT_STARTED
        try:
            person_data = (get_angel_of if person == ANGEL else get_mortal_of)(
                msg['from']['username'])
        except IndexError:
            print(f'Invalid username {msg["from"]["username"]}')
            return build_unauthorised_player_message(msg['from']['username'])
        if content_type == "sticker":
            sender_bot.sendSticker(person_data.chat_id, msg['sticker']['file_id'])
        elif content_type == "text":
            sender_bot.sendMessage(person_data.chat_id, message_text)
        # elif content_type == "photo":
        #     bot.sendPhoto(person_data.chat_id,
        #                   msg['photo'][0]['file_id'], caption=message_text)
        # elif content_type == "audio":
        #     bot.sendAudio(person_data.chat_id,
        #                   msg['audio']['file_id'], caption=message_text)
        # elif content_type == "video":
        #     bot.sendVideo(person_data.chat_id,
        #                   msg['video']['file_id'], caption=message_text)
        # elif content_type == "voice":
        #     bot.sendVoice(person_data.chat_id,
        #                   msg['voice']['file_id'], caption=message_text)
        # elif content_type == "video_note":
        #     bot.sendVideoNote(person_data.chat_id,
        #                       msg['video_note']['file_id'])
        else:       # unsupported file type, send error message from receiving bot
            receiver_bot.sendMessage(chat_id, build_invalid_content_type_message(
                content_type), reply_to_message_id=msg['message_id'])
            return f'Attempt to send unsupported content type ({content_type}) to {person}, {person_data.name}'
        return f'{content_type} sent to {person}, {person_data.name}'
    return send_to_person

############################### END SECTION: SEND TO PEOPLE ###############################


def help_me(receiver_bot, sender_bot, chat_id, msg, message_text):
    receiver_bot.sendMessage(chat_id, HELP_GUIDE, parse_mode='MarkdownV2')


def start(receiver_bot, sender_bot, chat_id, msg, message_text):
    receiver_bot.sendMessage(chat_id, START_GUIDE)
    receiver_bot.sendMessage(chat_id, HELP_GUIDE, parse_mode='MarkdownV2')

    try:
        player_data = groups[list(zip(
            *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
    except:
        return PLAYER_NOT_FOUND
    else:
        player_data.number_of_starts += 1   # possible bug if player sends /start to the same bot twice
        update_players_database()
        return f'Welcome {player_data.name}! Please proceed to send /start to the other bot ({os.environ.get("ANGEL_BOT_USERNAME")}, {os.environ.get("MORTAL_BOT_USERNAME")}) if you have not done so, then send /register to any of the 2 bots to confirm your registration.'


def start_game(receiver_bot, mortal_bot, angel_bot, chat_id, msg, message_text):
    global game_started
    if PASSWORD not in message_text:
        return 'Unauthorized.'
    print('Starting game...')
    for group in groups:
        for index, player in enumerate(group):
            mortal_bot.sendMessage(player.chat_id, GAME_STARTING_MORTAL_BOT)
            angel_bot.sendMessage(player.chat_id, GAME_STARTING_ANGEL_BOT)
            if index == GROUP_SIZE - 1:
                their_mortal = group[0]
            else:
                their_mortal = group[index+1]
            mortal_reveal_message = build_mortal_reveal_message(player.name, their_mortal)
            mortal_bot.sendMessage(player.chat_id, mortal_reveal_message)
            angel_bot.sendMessage(player.chat_id, START_GAME_MESSAGE_ANGEL_BOT)
    game_started = True
    with open('game_started.txt', 'w') as f:
        f.write('1')


def register(receiver_bot, sender_bot, chat_id, msg, message_text):      # to be understood
    try:
        player_data = groups[list(zip(
            *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
    except IndexError:
        return PLAYER_NOT_FOUND
    
    if player_data.number_of_starts >= 2:        # player has already sent /start to other bot
        receiver_bot.sendMessage(chat_id, build_registration_message(
            player_data), parse_mode='HTML')
    else:                                           # first time that player is sending /start to any of the 2 bots
        return (build_start_other_bot_message(player_data.name))



def verify(receiver_bot, sender_bot, chat_id, msg, message_text):        # to be understood
    player_data: Player = groups[list(zip(
        *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
    if player_data.number_of_starts >= 2:        # player has already sent /start to other bot
        player_data.update_chat_id(chat_id)
        update_players_database()
        print(
            f'Player {player_data.name} (username {player_data.username}) sucessfully registered!')
        print(check_registration(None, None, None, None, PASSWORD))
        return (build_verification_message(player_data.name))
    else:                                           # first time that player is sending /start to any of the 2 bots
        print(f'Player {player_data.name} (username {player_data.username}) registering without starting second bot')
        return (build_start_other_bot_message(player_data.name))

def update_username(receiver_bot, sender_bot, chat_id, msg, message_text):       # to be understood
    player_data = groups[list(
        zip(*np.where(np.vectorize(lambda x: x.chat_id)(groups) == chat_id)))[0]]
    # print(player_data.chat_id)
    try:
        assert (message_text == msg['from']['username'])
    except AssertionError:
        return build_unauthorized_username_error(message_text, msg['from']['username'])
    player_data.update_username(message_text)
    # print(player_data.chat_id)
    update_players_database()
    print(
        f'Player {player_data.name} updated their username to {player_data.username}!')
    return build_changed_username_message(player_data)
