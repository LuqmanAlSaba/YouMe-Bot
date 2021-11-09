import time
import keyboard
import pyautogui
import pydirectinput
import speech_recognition as sr
import pyaudio
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

screen_center = int(pydirectinput.size()[0] / 2.0), int(pydirectinput.size()[1] / 2.0)


# def q():
#


# Yuumi dashes to a target ally
def w(player):
    pydirectinput.keyDown(player)
    pydirectinput.moveTo(screen_center[0], screen_center[1] - 50, duration=0)
    keyboard.press_and_release('w')


# def e():
#


# def r():
#

# Yuumi performs the back action, detaching from allies if necessary
def back():
    data = get_data()
    attached_status = data['activePlayer']['abilities']['W']['id']
    if attached_status == 'YuumiWEndWrapper':
        pydirectinput.keyDown('w')
    pydirectinput.keyDown('b')


# Yuumi follows a target ally
def follow(player):
    pydirectinput.keyDown(player)
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


if __name__ == '__main__':
    # get live game data: https://127.0.0.1:2999/liveclientdata/allgamedata
    # https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api

    purchased_items = []
    item_path = [('Spellthief\'s Edge', 400), ('Faerie Charm', 250), ('Amplifying Tome', 435),
                 ('Bandleglass Mirror', 265), ('Ruby Crystal', 400), ('Kindlegem', 400)]

    # Below is code for testing the functions while we don't have VR working
    # We can add more functions to the if/else branch as we code them
    print("+---------------------------+")
    print("+       Select Option       +")
    print("+       W - W Ability       +")
    print("+       B - Recall          +")
    print("+       O - See Options     +")
    print("+       STOP - Stop Testing +")
    print("+---------------------------+")
    while True:
        choice = input()
        if choice == 'W':
            print("Executing W in 5 seconds, please open LoL...")
            time.sleep(5)
            w('f4')
        elif choice == 'B':
            print("Executing B in 5 seconds, please open LoL...")
            time.sleep(5)
            back()
        elif choice == 'O':
            print("+---------------------------+")
            print("+       Select Option       +")
            print("+       W - W Ability       +")
            print("+       B - Recall          +")
            print("+       O - See Options     +")
            print("+---------------------------+")
        elif choice == 'STOP':
            break
        else:
            print("Please select a valid option...")

    # follow('f3')
    # w('f4')
    # e()

    # Example voice recognition code that listens
    # for 5 seconds and prints the result
    r = sr.Recognizer()

    with sr.Microphone() as source:
        # read the audio data from the default microphone
        audio_data = r.record(source, duration=5)
        print("Recognizing...")
        # convert speech to text
        text = r.recognize_google(audio_data)
        print(text)
