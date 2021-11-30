import time
import keyboard
import pyautogui
import pydirectinput
import speech_recognition
import speech_recognition as sr
import pyaudio
import requests
from urllib3.exceptions import InsecureRequestWarning
import threading
import random

# get live game data: https://127.0.0.1:2999/liveclientdata/allgamedata
# https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

screen_center = int(pydirectinput.size()[0] / 2.0), int(pydirectinput.size()[1] / 2.0)

purchased_items = []
item_path = [('Spellthief\'s Edge', 400), ('Faerie Charm', 250), ('Amplifying Tome', 435), ('Bandleglass Mirror', 265), ('Ruby Crystal', 400), ('Kindlegem', 400), ('Moonstone Renewer', 750),
             ('Amplifying Tome', 435), ('Oblivion Orb', 400), ('Faerie Charm', 250), ('Amplifying Tome', 435), ('Bandleglass Mirror', 265), ('Chemtech Putrifier', 550),
             ('Amplifying Tome', 435), ('Faerie Charm', 250), ('Forbidden Idol', 550), ('Amplifying Tome', 435), ('Ardent Censer', 630),
             ('Amplifying Tome', 435), ('Faerie Charm', 250), ('Forbidden Idol', 550), ('Amplifying Tome', 435), ('Staff of Flowing Water', 630),
             ('Faerie Charm', 250), ('Forbidden Idol', 550), ('Null-Magic Mantle', 450), ('Negatron Cloak', 450), ('Mikael\'s Blessing', 600),
             ('Dark Seal', 350), ('Mejai\'s Soulstealer', 1250)]

roles = {
        'top': 'f1',
        'jungle': 'f2',
        'mid': 'f3',
        'adc': 'f4',
        'support': 'f5'
    }


def q():
    keyboard.press_and_release('q')


# Yuumi dashes to a target ally when given an allies position
# example: w jungle
def w(position):
    pydirectinput.keyDown(roles[position])
    pydirectinput.moveTo(screen_center[0], screen_center[1] - 50, duration=0)
    keyboard.press_and_release('w')


def e():
    keyboard.press_and_release('e')



# def r():
#


# Yuumi performs the back action, detaching from allies if necessary
def back():
    data = get_data()
    try:
        attached_status = data['activePlayer']['abilities']['W']['id']
        if attached_status == 'YuumiWEndWrapper':
            pydirectinput.press('w')
    except TypeError:
        print("Not in game")
    pydirectinput.press('b')


def ward():
    pydirectinput.moveTo(screen_center[0] - 10, screen_center[1] + 25)
    pydirectinput.keyDown('4')


# Yuumi follows a target ally when given an allies position
# example: follow jungle
def follow(position):
    pydirectinput.keyDown(roles[position])
    pydirectinput.keyDown('x')
    pydirectinput.rightClick(screen_center[0] - 10, screen_center[1] + 25, duration=10000)


# Yuumi purchases items from her item path
def buy():
    data = get_data()
    current_gold = data['activePlayer']['currentGold']
    pydirectinput.press('p')

    while len(item_path) > 0 and current_gold > item_path[0][1]:
        pydirectinput.keyDown('ctrl')
        pydirectinput.keyDown('l')
        pydirectinput.keyUp('ctrl')
        pydirectinput.keyUp('l')

        pyautogui.write(item_path[0][0])
        current_gold -= item_path[0][1]

        purchased_items.append(item_path.pop(0))
        keyboard.press_and_release('enter')
    pydirectinput.press('esc')


# gets game data
def get_data():
    try:
        url = "https://127.0.0.1:2999/liveclientdata/allgamedata"
        r = requests.get(url, verify=False)
        data = r.json()
        print("JSON: ", data)
        print(data['activePlayer']['currentGold'])
        return data
    except requests.exceptions.ConnectionError:
        print("Game has ended.")


def level_up_abilities():
    kill_messages = ['nice!', 'ez', ':)', 'gj', 'well played', 'FF', 'SO EZ']
    ability_order = ["q", "e", "e", "q", "e", "r", "e", "q", "e", "r", "q", "q", "w", "w", "r", "w", "w"]
    yuumi_level = 0
    team_kills = 0
    while True:
        data = get_data()

        current_level = int(data['activePlayer']['level'])
        current_team_kills = 0

        # if yuumi has leveled up
        if current_level != yuumi_level:
            # level up next ability in queue
            next_ability = ability_order.pop(0)
            pydirectinput.keyDown('ctrl')
            pydirectinput.keyDown(next_ability)
            pydirectinput.keyUp('ctrl')
            pydirectinput.keyUp(next_ability)
            yuumi_level += 1

        # get updated team kills
        for player in data['allPlayers']:
            current_team_kills += int(player['scores']['kills'])

        # if team gets a kill
        if team_kills != current_team_kills:
            # emote
            pydirectinput.press('t')
            # Type message in chat
            pydirectinput.press('enter')
            pyautogui.write('/all ' + random.choice(kill_messages))
            pydirectinput.press('enter')
        time.sleep(2)