import os
import sys
import speech_recognition
import speech_recognition as sr
import threading
import wave  # for audio playback (testing purposes)
from datetime import datetime, timedelta
import pyaudio
from heapq import heappush, heappop
from Yuumi import *


class YouMeSpeechRecognizer:
    # Chunk size for reading audio during playback
    chunk = 1024
    # Allow only one thread to access audio output
    audio_mutex = threading.Lock()

    # output_stream will contain the parsed speech as output
    # each word will be separated by one or more spaces
    # output will be in order that input speech is spoken
    # playback will enable audio playback for testing purposes
    def __init__(self, output_stream, playback=False):
        self.output_stream = output_stream
        self.playback = playback

        self.r = sr.Recognizer()
        self.r.phrase_threshold = 0.20  # minimum seconds of speaking audio before we consider the speaking audio a
        # phrase - values below this are ignored (for filtering out clicks and pops)

        self.r.pause_threshold = 0.20  # seconds of non-speaking audio before a phrase is considered complete
        self.r.non_speaking_duration = 0.12  # seconds of non-speaking audio to keep on both sides of the recording

        self.mic = sr.Microphone()

        if self.playback:
            self.p_audio = pyaudio.PyAudio()

        # automatically adjust ambient energy threshold every x seconds
        self.time_between_ambient_adjustments = timedelta(seconds=120)
        self.last_adjust_time = datetime.min

        # Thread counting and ordered output
        self.cnt = 0
        self.last_popped = 0
        self.pq = []
        # Allow only one thread to access pq and output stream
        self.out_lock = threading.Lock()

    # called by thread
    def __call__(self):
        with self.mic as source:
            while True:
                if datetime.now() - self.last_adjust_time > self.time_between_ambient_adjustments:
                    print("Adjusting for ambient noise...")
                    self.last_adjust_time = datetime.now()
                    self.r.adjust_for_ambient_noise(source)
                self.cnt += 1
                cnt = self.cnt
                print("(" + str(cnt) + ") Listening for input")
                audio = self.r.listen(source)
                if self.playback:
                    playback_thread = threading.Thread(target=self.playback_audio, args=(audio, cnt))
                    playback_thread.start()

                print("(" + str(cnt) + ") Parsing input")
                parse_thread = threading.Thread(target=self.parse_speech, args=(audio, cnt))
                parse_thread.start()

    def __exit__(self):
        print("exit called")
        if self.playback:
            self.p_audio.terminate()

    # Parse the speech contained in audio
    # Store this speech in pq with the form (cnt, text)
    # Call write_out() to write stored inputs in order
    def parse_speech(self, audio, cnt):
        try:
            text = self.r.recognize_google(audio)
            print("(" + str(cnt) + ") Voice input recognized: " + text)
            heappush(self.pq, (cnt, text + ' '))
            self.write_out()
        except speech_recognition.UnknownValueError:
            print("(" + str(cnt) + ") Speech not recognized...")
            heappush(self.pq, (cnt, ""))

    # output voice commands in order in which they were spoken
    # (not the order in which they were parsed)
    def write_out(self):
        with self.out_lock:
            while len(self.pq) > 0 and self.pq[0][0] == self.last_popped + 1:
                out_text = heappop(self.pq)[1]
                print("Out_Text", out_text)

                if out_text == "bye " or out_text == "buy ":
                    buy()
                elif out_text == "back ":
                    back()
                elif out_text == "q " or out_text == "Q ":
                    q()
                elif out_text == "w ":
                    w('f4')
                elif out_text == "speed ":
                    e()
                elif out_text == "follow ":
                    follow('f3')

                self.output_stream.write(out_text)
                self.output_stream.flush()
                self.last_popped += 1

    # Playback recorded audio for testing
    def playback_audio(self, audio, cnt):
        with self.audio_mutex:  # Ensure only one concurrent thread writing to audio output
            print("(" + str(cnt) + ") Playing back audio")
            # There is surely a better way than writing to file then reading from file, but this works
            with open('speech.wav', 'wb') as f:
                f.write(audio.get_wav_data())
            wf = wave.open('speech.wav', 'rb')
            stream = self.p_audio.open(
                format=self.p_audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            data = wf.readframes(self.chunk)
            while data != b'':
                stream.write(data)
                data = wf.readframes(self.chunk)
            stream.close()
            wf.close()
            print("(" + str(cnt) + ") Playback done")
            os.remove('speech.wav')


if __name__ == '__main__':
    ym_sr = YouMeSpeechRecognizer(sys.stdout, playback=False)  # playback is just for testing
    t = threading.Thread(target=ym_sr)
    t.start()  # Run voice input on separate thread

    level_abilities_thread = threading.Thread(target=level_up_abilities)
    level_abilities_thread.start()  # Run ability leveling thread
