import speech_recognition as sr
import pyaudio

def driver(command):
    if command == 'w':
        print("Executing W in 5 seconds, please open LoL...")
        time.sleep(5)
        w('f4')
    elif command = 'b':
        print("Executing B in 5 seconds, please open LoL...")
        time.sleep(5)
        back()
    else:
        #dunno probs some time in between commands






def vr():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, duration=5)
        text = r.recognize_google(audio)

        driver(text)

if __name__ == '__main__':
    while True:
        vr()
