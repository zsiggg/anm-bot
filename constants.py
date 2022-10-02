import os
from dotenv import load_dotenv
load_dotenv()

### USED IN functions.py ###

GROUP_SIZE = 8  # EDIT THIS
PASSWORD = os.environ.get('PASSWORD')

ANGEL = "🕊ANGEL🕊"
MORTAL = "🐵MORTAL🐵"

GAME_NOT_STARTED = 'The game has not started yet, please be patient ⏰⏳!'

GAME_STARTING_ANGEL_BOT = 'Looking for your angel...'

GAME_STARTING_MORTAL_BOT = 'Looking for your mortal...'

PLAYER_NOT_FOUND = 'Player not found. Either fill up the Google Form, or contact house comm members for assistance.'

START_GUIDE = '''HOOTHOOT\\!\\! Welcome to Rusa's 🕊 Angel and 🐵 Mortal\\!\\! This bot 🤖🤖 is created and designed by @richard_dominick\\. He is an incredible fellow, please thank him if you do see him around\\!

A reminder that you’re 🚫NOT🚫 allowed to enter anybody’s room at all times\\! Gifting is to be done ❌WITHOUT❌ risk of spreading infectious diseases and with minimal contact😷🤒\\!\\! And keep in mind OHS regulations regarding damage to property and COVID 1️⃣9️⃣\\!\\!\\! 

HAVE FUN AND STAY SAFE\\!\\!'''

HELP_GUIDE = '''*Rusa Angels and Mortals Bot Help Guide*

Rusa Angel and Mortals are back for another year 💪💪 

Now, there are separate bots to talk to your Angel and Mortal\\. Talk to your Angel 👼🏻 in the Angel bot, and your Mortal 👶🏻 in the Mortal bot\\! Simply start sending a message or sticker ✨, and your angel or mortal should receive it\\!

*Commands*
`/help      `: brings up this page
`/register  `: begins the registration process

*What does not work*
Tele Bubbles, videos, photos, or any kinds of media or files
Replying messages, reactions to messages \\(your angel/mortal won't be able to see this even if you can\\!\\)

If the bot does not acknowledge your message, please give it some time as the server may be experiencing high traffic/demand 🙁\\. For tech support please contact house comm members\\.
'''
START_GAME_MESSAGE_ANGEL_BOT = 'Your chat with your angel has started! Say hi 👋'


def build_unauthorised_player_message(player_name):
    return f'ERROR: Unauthorised player!\n\nI\'m sorry, I don\'t recognise you. Did you change your username? If you did, please send "/update <new_username>" here first. Replace <new_username> with your current username (e.g. "/update {player_name}").\n\nIf you did not change your username but are still getting this error, please contact tech support!'


def build_message(type, player_name, content, person):
    end = f'\n\nType {["/m", "/a"][person == ANGEL]} or {["/mortal", "/angel"][person == ANGEL]}, followed by your message, to reply.\nExample: "{["/m", "/a"][person == ANGEL]} hi!" {["#mortal", "#angel"][person == ANGEL]}'
    if type == 'text':
        return f'✍️ Hi {player_name}, your {person} sent you a message:\n\n"{content}"' + end
    elif type == 'photo':
        return f'✍️ Hi {player_name}, your {person} sent you a photo with the following caption:\n\n"{content}"' + end


def build_mortal_reveal_message(player_name, their_mortal):
    return f'Hi {player_name}, we have found your mortal, {their_mortal.name}! These are their details:\n\nFun Fact: {their_mortal.fun_fact}\nFavourites: {their_mortal.favourites}\nComfortable with pranks?: {their_mortal.open_to_pranks}\nDieterary preferences:{their_mortal.diet_pref}\nNotes for Angel: {their_mortal.note_for_angel}\n\nHappy texting!'


def build_registration_message(player_data):
    return f'Please verify the following information:\n\n<b>Name:</b> {player_data.name}\n<b>Fun Fact:</b> {player_data.fun_fact}\n<b>Favourites:</b> {player_data.favourites}\n<b>Comfortable with pranks?:</b> {player_data.open_to_pranks}\n<b>Dieterary preferences:</b>{player_data.diet_pref}\n<b>Notes for Angel:</b> {player_data.note_for_angel}\n\n\nReply with /verify to verify.'


def build_verification_message(player_name):
    return f'Hi {player_name}, you have been successfully registered! Please wait for everyone else to finish their registration process. Once it is completed, the game will automatically start, and 🤖 I\'ll let you know who your {MORTAL} is!'


def build_changed_username_message(player_data):
    return f'Hi {player_data.name}, you have successfully updated your username to {player_data.username}!'


def build_unauthorized_username_error(new_username, actual_username):
    return f'Error: Not allowed! You are trying to update your username to {new_username}, but your current username is {actual_username}!\n\nPlease only send "/update <replace_this_with_your_new_username>" AFTER you have updated your username.\ne.g. "/update {actual_username}"'


def build_invalid_content_type_message(content_type):
    return f'This content type ({content_type}) is not supported!'


def build_start_other_bot_message(player_name):
    return f'Hi {player_name}, you have not started the other bot. Please go to either {os.environ.get("ANGEL_BOT_USERNAME")} or {os.environ.get("MORTAL_BOT_USERNAME")} and send /start before sending /register and /verify!'