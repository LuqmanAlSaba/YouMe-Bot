
class YouMeCommandStream:

    # function for appending text to command queue

        # (do we need a queue? should we wait for command to finish before executing another?
        #  i'd assume so, since commands involve output over time, multiple running at once is bad
        #  but we don't want to stop parsing commands while running a command

    # essentially wraps an IOStream, but instead of writing to a file,
    # writes to a "command text" buffer and enqueues valid commands
    # commands are executed in-order as soon as they are added to the command queue
    # a command is specified by an exact string match (not case sensitive)
    # when a command is matched, the corresponding function is run
    def __init__(self, command_dict, buffering=False):
        # queue of function calls
        self.function_call_queue = []
        # buffer for storing voice input, word-by-word
        self.word_buffer = []
        # dictionary of valid commands
        self.command_dict = command_dict


    def write(self, text):
        for word in text.split():
            self.word_buffer.append(word)

    def flush(self):
        # greedily try building commands
        print("flush")

    # way to specify valid commands

    # way to tie commands to function calls with arguments

if __name__ == '__main__':
    def back(args):
        print("back command call")

    def buy(args):
        print("buy command call with arg: " + args)

    def follow(args):
        print("follow command called with arg: " + args)

    command_dict_example = {
        "back": back,
        "buy": buy,
        "follow": follow
    }

    command_dict_example["follow"]("arg1")

    # ym_cs = YouMeCommandStream(command_dict_example)
