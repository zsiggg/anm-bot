import csv
import pickle
from random import randint, shuffle

import numpy as np
import telepot

from constants import *

class Player():
    def __init__(self, name, username, diet_pref, favourites, note_for_angel, fun_fact, open_to_pranks, chat_id = None, started_in_angel_bot = False, started_in_mortal_bot = False):
        self.started_in_angel_bot = started_in_angel_bot   # True if /start command run in angel bot
        self.started_in_mortal_bot = started_in_mortal_bot   # True if /start command run in mortal bot
        self.chat_id = chat_id     # this will be set later on with update_chat_id, after registration and verification
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


# writes the global variable groups into a .pickle file; called when groups is changed
def update_players_database():      
    with open('tmp/players.pickle', 'wb') as f:
        pickle.dump(groups, f)


############################### SECTION: ADMIN FUNCTIONS (PASSWORD REQUIRED) ###############################
def reload_players_data(receiver_bot, sender_bot, chat_id, msg, message_text):
    if PASSWORD not in message_text:
        return 'Unauthorized.'

    global groups
    groups = []
    with open('players.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            groups += [[Player(*(row[7*i:7*(i+1)]))
                        for i in range(GROUP_SIZE)]]
    groups = np.array(groups)
    update_players_database()

    global game_started
    game_started = False
    with open('game_started.txt', 'w') as f:
        f.write('0')

    return f'Players data successfully reloaded! {len(groups)} groups of {GROUP_SIZE} found.'


# check if all palyer's chat id has been recorded (occurs after registration and verification)
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
            mortal_bot.sendMessage(player.chat_id, mortal_reveal_message, parse_mode='HTML')
            angel_bot.sendMessage(player.chat_id, START_GAME_MESSAGE_ANGEL_BOT)
    game_started = True
    with open('game_started.txt', 'w') as f:
        f.write('1')


# sends a custom message ALL players
def announce(receiver_bot, sender_bot, chat_id, msg, message_text):      
    if PASSWORD not in message_text:
        return 'Unauthorized.'

    message_text_split = message_text.split()
    if len(message_text_split) < 2:
        return 'Enter an announcement to be made after the password'
    announcement = message_text_split[1]

    for group in groups:
        for player in group:
            receiver_bot.sendMessage(
                player.chat_id, f'Hi {player.name}, House Comm has made a new ANNOUNCEMENT, see below:\n\n{announcement}')
    return 'Your announcement has been broadcasted to everyone!'


# sends a message to all players revealing their own group numbers
def reveal(receiver_bot, sender_bot, chat_id, msg, message_text):
    if PASSWORD not in message_text:
        return 'Unauthorized.'

    for group_index, group in enumerate(groups):
        for player in group:
            receiver_bot.sendMessage(player.chat_id, f'<b>???THE BIG REVEAL???</b>\n\nHi {player.name}, thank you for participating in Rusa Angels and Mortals! As we bring this event to a close, we invite you to come to THE LAWN from 8-10pm TONIGHT ????\n\nAre you excited to find out who your angel is? Hint - you may find this group number helpful: <code>{group_index + 1}</code>\n\nSee you guys there! ????????', parse_mode='HTML')
    return 'Pairings revealed!'
############################### END SECTION: ADMIN FUNCTIONS (PASSWORD REQUIRED) ###############################


############################### SECTION: SEND TO PEOPLE ###############################
def get_angel_of(player_username):
    return groups[tuple((np.array(list(zip(*np.where(np.vectorize(lambda x: x.username.strip())(groups) == player_username)))[0]) - [0, 1]) % [len(groups), GROUP_SIZE])]


def get_mortal_of(player_username):
    return groups[tuple((np.array(list(zip(*np.where(np.vectorize(lambda x: x.username.strip())(groups) == player_username)))[0]) + [0, 1]) % [len(groups), GROUP_SIZE])]


def send_to_person(person_type, receiver_bot, sender_bot, chat_id, msg, message_text, content_type):
    try:
        person_data = (get_angel_of if person_type == ANGEL else get_mortal_of)(
            msg['from']['username'])
    except IndexError:
        receiver_bot.sendMessage(chat_id, build_unauthorised_player_message(msg['from']['username']))
        return f'Invalid username {msg["from"]["username"]}'

    if not game_started:
        receiver_bot.sendMessage(chat_id, GAME_NOT_STARTED)
        sender_data = groups[list(zip(
            *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
        if sender_data.chat_id is None:
            receiver_bot.sendMessage(chat_id, 'It seems like you have not registered. Send /register and follow the instructions!')
        return f'{sender_data.name} tried to send message before game started'

    if content_type in ['sticker', 'text']:     # TO BE SENT TO USER DIRECTLY
        if content_type == "sticker":
            sender_bot.sendSticker(person_data.chat_id, msg['sticker']['file_id'])
        elif content_type == "text":
            sender_bot.sendMessage(person_data.chat_id, message_text)
        return f'{content_type} sent to {person_type}, {person_data.name}'
    else:                                       # FILES; TO BE FORWARDED TO FILES CHANNEL
        if content_type in ['photo', 'audio', 'video', 'voice', 'video_note', 'document']:      # supported file types               
            receiver_bot.forwardMessage(os.environ.get('FILES_CHANNEL_ID'), chat_id, msg['message_id'])
            return f'Forwarded {content_type} for {person_type}, {person_data.name} to files channel'
        else:                                                                       # unsupported file type, send error message from receiving bot
            receiver_bot.sendMessage(chat_id, build_invalid_content_type_message(
                content_type), reply_to_message_id=msg['message_id'])
            return f'Attempt to send unsupported content type ({content_type}) to {person_type}, {person_data.name}'

def send_file_from_channel(msg, receiver_bot, sender_bot, receiver):
    # bot 1 that received the original message forwards the message to channel
    # but only bot 2 that did not forward the message receives the message from the channel
    # in the original context of the user's message, bot 1 = receiver_bot, bot 2 = sender_bot
    # however when receiving the file from the file channel, bot 2 = receiver_bot, bot 1 = sender_bot
    # thus, we need to swap receiver_bot, sender_bot and receiver
    channel_receiver_bot = receiver_bot
    receiver_bot, sender_bot = sender_bot, receiver_bot
    receiver = ANGEL if receiver == MORTAL else MORTAL

    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type in ['text', 'sticker']:
        channel_receiver_bot.deleteMessage(telepot.message_identifier(msg))
        return 'ERROR! Text and stickers should not be received from files channel'

    if msg.get('forward_from', None) == None:
        channel_receiver_bot.deleteMessage(telepot.message_identifier(msg))
        return 'ERROR! Files must be forwarded from somewhere to be successfully sent.'
    
    if content_type not in ['photo', 'audio', 'video', 'voice', 'video_note', 'document']:
        channel_receiver_bot.deleteMessage(telepot.message_identifier(msg))
        return 'ERROR! Unsupported file type received in files channel.'

    try:
        person_data = (get_angel_of if receiver == ANGEL else get_mortal_of)(
            msg['forward_from']['username'])
    except IndexError:
        receiver_bot.sendMessage(chat_id, build_unauthorised_player_message(msg['forward_from']['username']))
        return f'Invalid username {msg["forward_from"]["username"]}'

    print(f'Sending {content_type} to {receiver}, {person_data.name} from files channel')

    if content_type == 'photo':
        sender_bot.sendPhoto(person_data.chat_id,
            msg['photo'][0]['file_id'], caption=msg.get('caption', ''))
    elif content_type == 'audio':
        sender_bot.sendAudio(person_data.chat_id,
            msg['audio']['file_id'], caption=msg.get('caption', ''))
    elif content_type == 'video':
        sender_bot.sendVideo(person_data.chat_id,
            msg['video']['file_id'], caption=msg.get('caption', ''))
    elif content_type == 'voice':
        sender_bot.sendVoice(person_data.chat_id,
            msg['voice']['file_id'], caption=msg.get('caption', ''))
    elif content_type == 'video_note':
        sender_bot.sendVideoNote(person_data.chat_id,
            msg['video_note']['file_id'])
    elif content_type == 'document':
        sender_bot.sendDocument(person_data.chat_id,
            msg['document']['file_id'], caption=msg.get('caption', ''))
    else:
        print(f'ERROR! No function is provided for valid file type {content_type}')

    channel_receiver_bot.deleteMessage(telepot.message_identifier(msg))
############################### END SECTION: SEND TO PEOPLE ###############################


############################### SECTION: OTHER COMMANDS ###############################
def help_me(receiver_bot, sender_bot, chat_id, msg, message_text):
    receiver_bot.sendMessage(chat_id, HELP_GUIDE, parse_mode='MarkdownV2')


def start(receiver_bot, sender_bot, chat_id, msg, message_text, receiver):
    receiver_bot.sendMessage(chat_id, START_GUIDE)
    receiver_bot.sendMessage(chat_id, HELP_GUIDE, parse_mode='MarkdownV2')

    try:
        player_data = groups[list(zip(
            *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
    except:
        return PLAYER_NOT_FOUND
    else:
        if receiver == ANGEL:
            player_data.started_in_angel_bot = True
        else:
            player_data.started_in_mortal_bot = True
        update_players_database()
        return f'Welcome {player_data.name}! Please proceed to send /start to the other bot ({os.environ.get("ANGEL_BOT_USERNAME")}, {os.environ.get("MORTAL_BOT_USERNAME")}) if you have not done so, then send /register to any of the 2 bots to confirm your registration.'


def register(receiver_bot, sender_bot, chat_id, msg, message_text):      
    try:
        player_data: Player = groups[list(zip(
            *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
    except IndexError:
        return PLAYER_NOT_FOUND
    
    if player_data.started_in_angel_bot and player_data.started_in_mortal_bot:        # player sent start in both bots
        receiver_bot.sendMessage(chat_id, build_registration_message(
            player_data), parse_mode='HTML')
    else:                                           # player only sent /start to 1 bot
        return (build_start_other_bot_message(player_data.name))



def verify(receiver_bot, sender_bot, chat_id, msg, message_text):        
    player_data: Player = groups[list(zip(
        *np.where(np.vectorize(lambda x: x.username.strip())(groups) == msg['from']['username'])))[0]]
    if player_data.started_in_angel_bot and player_data.started_in_mortal_bot:        # player sent start in both bots
        player_data.update_chat_id(chat_id)
        update_players_database()
        print(
            f'Player {player_data.name} (username {player_data.username}) sucessfully registered and verified!')
        print(check_registration(None, None, None, None, PASSWORD))
        return (build_verification_message(player_data.name))
    else:                                           # player only sent /start to 1 bot
        print(f'Player {player_data.name} (username {player_data.username}) attempting to verify without starting second bot')
        return (build_start_other_bot_message(player_data.name))

# updates any field of a Player
def update(receiver_bot, sender_bot, chat_id, msg, message_text):       
    [password, username, field_name, new_field_value] = message_text.split('|')
    if password != PASSWORD:
        return 'Unauthorised.'
    try:
        player_data = groups[list(
            zip(*np.where(np.vectorize(lambda x: x.username)(groups) == username)))[0]]
    except IndexError:
        return PLAYER_NOT_FOUND
    # print(player_data.chat_id)
    # try:
    #     assert (message_text == msg['from']['username'])
    # except AssertionError:
    #     return build_unauthorized_username_error(message_text, msg['from']['username'])
    try:
        old_field_value = getattr(player_data, field_name)
    except AttributeError:
        return f'There is no such field as {field_name}'

    setattr(player_data, field_name, new_field_value)
    # print(player_data.chat_id)
    # receiver_bot.sendMessage(chat_id, build_changed_username_message(player_data))
    update_players_database()
    return (
        f'Updated {field_name} of {player_data.name} from {old_field_value} to {getattr(player_data, field_name)}!')
############################### SECTION: OTHER COMMANDS ###############################


# MAIN CODE FOR TESTING (comment out if in production)
# groups = np.array([[Player('Zsigmond', 'zsiggg', 'everything', 'for you to find out', 'none', 'im fun', 'true', <chat_id>, True, True), 
#     Player('Zsigmond', 'zsiggg', 'everything', 'for you to find out', 'none', 'im fun', 'true', <chat_id>, True, True), ], ])

# MAIN CODE FOR REAL USE (comment out if testing)
reload_players_data(None, None, None, None, PASSWORD)

with open('tmp/players.pickle', 'rb') as f:
    groups = pickle.load(f)

game_started = False
if os.path.exists('game_started.txt'):
    with open('game_started.txt', 'r') as f:        # read previous game_started
        game_started = int(f.read())
else:
    with open('game_started.txt', 'w') as f:        # create game_started.txt if not created
        f.write('0')

