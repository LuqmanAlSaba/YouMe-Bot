# essentially wraps an IOStream, but instead of writing to a file or buffer,
# takes the input and turns it into function calls.

import queue
import threading
from datetime import datetime, timedelta


class YouMeCommandStream:

    # this implementation writes to a "command text" buffer and enqueues valid commands.
    # commands are executed in-order as soon as they are added to the command queue
    # a command is specified by an exact string match (not case-sensitive)
    # when a command is matched, the corresponding function is run
    #
    # command_dict: dictionary of valid commands. mapping of command_text => function_callback
    # when a command is matched, the corresponding function is called
    # all the text after that command is passed as a string argument
    def __init__(self, command_dict):
        # queue of function calls. queue.Queue is a thread-safe object
        self.function_call_queue = queue.Queue
        # command queue lock for concurrent access
        self.function_call_lock = threading.Lock()

        # buffer for storing voice input, word-by-word
        # related functions could be more efficiently implemented but for our purposes this is perfectly fine
        self.word_buffer = []
        # buffer lock for concurrent access
        self.word_buffer_lock = threading.Lock()

        # dictionary of valid commands
        self.command_dict = command_dict
        self.longest_command_length = -1
        for key in command_dict.keys():
            self.longest_command_length = max(self.longest_command_length, len(key.split()))

        # We don't want to clean input too soon, but we also need to remove unused input from the buffer eventually.
        # If the age of an input exceeds this amount of time, it will be cleaned automatically after the next flush.
        self.max_input_age = timedelta(seconds=3)

    def write(self, text):
        print("  Writing to command stream: " + text)
        with self.word_buffer_lock:
            for word in text.split():
                # [word, timestamp]
                self.word_buffer.append([word, datetime.now()])
        self.flush()

    def clean_buffer(self):
        print("  Cleaning command stream's buffer")
        with self.word_buffer_lock:
            offset = 0
            for word_index in range(0, len(self.word_buffer)):
                word_index -= offset
                timestamp = self.word_buffer[word_index][1]
                if datetime.now() - timestamp > self.max_input_age:
                    print("Removing " + self.word_buffer[word_index][0] + " from command stream's buffer due to age")
                    del self.word_buffer[word_index]
                    offset += 1

    def flush(self):
        # greedily try building commands
        # we will always try to match the latest input first,
        # starting with the longest commands and ending with the shortest.
        #
        # if another command's text appears after a command, it will call that more recent command text,
        # then the earlier command.
        # this may produce unintended results, such as if a command's text is supposed to be an argument for a prior
        # command.
        #
        # "end" starts at end of buffer
        # "begin" is always at at max(0, end - self.longest_command_length)
        # basically "begin" and "end" are moved backwards until "begin" reaches the beginning of the word buffer,
        # then, "end" is moved backwards until it reaches the beginning of the word buffer
        # for each iteration, every prefix in the substring with bounds defined by the range [begin, end]
        #   is queried in the command dictionary, beginning with the longest substring
        print("  Flushing command stream's buffer")
        command_executed = False
        with self.word_buffer_lock:
            for end in range(len(self.word_buffer), 0, -1):
                begin = max(0, end - self.longest_command_length)

                # cmd is substring from begin to end
                cmd = " ".join(word[0] for word in self.word_buffer[begin:end])

                # query dictionary based on cmd
                if cmd not in self.command_dict:
                    continue
                func = self.command_dict[cmd]

                # args will be the rest of the word buffer (the text directly after the command)
                # again, ugly list zip stuff
                args = " ".join(word[0] for word in self.word_buffer[end:])

                # Make the function call.
                # Not going on a separate thread to make the function call. Assuming all functions are exclusive.
                print("  Calling " + func.__name__ + "(" + args + ") from command stream")
                func(args)

                # "Pop" the executed command from the word buffer after it is complete.
                self.word_buffer = self.word_buffer[:begin]
                command_executed = True
                break

        if not command_executed:
            # done with buffer: clean and return
            self.clean_buffer()
            return

        # a command was executed: continue parsing less recently spoken commands
        self.flush()


if __name__ == '__main__':
    def back(args):
        print("Back called with args='" + args + "'")


    def buy(args):
        print("Buy called with args='" + args + "'")


    def follow(args):
        print("Follow called with args='" + args + "'")


    command_dict_example = {
        "back": back,
        "buy": buy,
        "follow": follow
    }

    ym_cs = YouMeCommandStream(command_dict_example)

    ym_cs.write("hi")
    ym_cs.write("back")

    inputs = ["follow", "follow four", "buy golden blade", "buy golden follow 4"]
    for i in inputs:
        ym_cs.write(i)
        print()

    # grab input from command line for testing
    while True:
        string = input()
        ym_cs.write(string)
