

### USED IN functions.py ###

PASSWORD = 'halimahandherdeers'  # FILL THIS UP

ANGEL = "🕊ANGEL🕊"
MORTAL = "🐵MORTAL🐵"

GAME_NOT_STARTED = 'The game has not started yet, please be patient ⏰⏳!'

GAME_STARTING = 'Looking for your mortal...'

PLAYER_NOT_FOUND = 'Player not found. Either fill up the Google Form, or contact house comm members for assistance.'

START_GUIDE = '''HOOTHOOT‼️‼️ Welcome to Strix’s 🕊 Angel and 🐵 Mortal!! This bot 🤖🤖 is created and designed by @richard_dominick. He is an incredible fellow, please thank him if you do see him around!

A reminder that you’re 🚫NOT🚫 allowed to enter anybody’s room at all times! Gifting is to be done ❌WITHOUT❌ risk of spreading infectious diseases and with minimal contact😷🤒!! And keep in mind OHS regulations regarding damage to property and COVID 1️⃣9️⃣!!! 

HAVE FUN AND STAY SAFE!!'''

HELP_GUIDE = '''*Strix Angels and Mortals Bot Help Guide*
To view your chat history, feel free to use the \\#angel or \\#mortal hashtags attached\\.

`/help      `: brings up this page
`/a, /angel `: sends a message anonymously to your angel,
`/m, /mortal`: sends a message anonymously to your mortal,
`/register  `: begins the registration process

You can also send photos and stickers using this bot, in addition to text messages\\.

*Command Syntax*
`/help`
`/a <message>`
`/angel <message>`
`/m <message>`
`/mortal <message>`
`/register`

If the bot does not acknowledge your message, please give it some time as the server may be experiencing high traffic/demand\\. For tech support please contact house comm members\\.

_Tip: On mobile, you can press and hold the commands \\(e\\.g\\. /a, /m\\) to start a new message beginning with that command\\._'''


def build_unauthorised_player_message(player_name):
    return f'ERROR: Unauthorised player!\n\nI\'m sorry, I don\'t recognise you. Did you change your username? If you did, please send "/update <new_username>" here first. Replace <new_username> with your current username (e.g. "/update {player_name}").\n\nIf you did not change your username but are still getting this error, please contact tech support!'


def build_message(type, player_name, content, person):
    end = f'\n\nType {["/m", "/a"][person == ANGEL]} or {["/mortal", "/angel"][person == ANGEL]}, followed by your message, to reply.\nExample: "{["/m", "/a"][person == ANGEL]} hi!" {["#mortal", "#angel"][person == ANGEL]}'
    if type == 'text':
        return f'✍️ Hi {player_name}, your {person} sent you a message:\n\n"{content}"' + end
    elif type == 'photo':
        return f'✍️ Hi {player_name}, your {person} sent you a photo with the following caption:\n\n"{content}"' + end


def build_mortal_reveal_message(player_name, their_mortal):
    return f'Hi {player_name}, we have found your mortal, {their_mortal.name}!\n\nThey are staying at B{their_mortal.room}.\n\nPlease do note that they have the following dietary preferences: {their_mortal.diet_pref}\n\nRemember to message your mortal anonymously by sending /m or /mortal, followed by your message (e.g. "/m hi!"). Likewise, should you want to message your angel, type /a or /angel, followed by your message.'


def build_registration_message(player_data):
    return f'Please verify the following information:\n\n<b>Name:</b> {player_data.name}\n<b>Year:</b> {player_data.year}\n<b>Room:</b> {player_data.room}\n<b>Dietary Preferences:</b> {player_data.diet_pref}\n\nReply with /verify to verify.'


def build_verification_message(player_name):
    return f'Hi {player_name}, you have been successfully registered! Please wait for everyone else to finish their registration process. Once it is completed, the game will automatically start, and 🤖 I\'ll let you know who your {MORTAL} is!'


def build_changed_username_message(player_data):
    return f'Hi {player_data.name}, you have successfully updated your username to {player_data.username}!'


def build_unauthorized_username_error(new_username, actual_username):
    return f'Error: Not allowed! You are trying to update your username to {new_username}, but your current username is {actual_username}!\n\nPlease only send "/update <replace_this_with_your_new_username>" AFTER you have updated your username.\ne.g. "/update {actual_username}"'


def build_invalid_content_type_message(content_type):
    return f'This content type ({content_type}) is not supported!'
