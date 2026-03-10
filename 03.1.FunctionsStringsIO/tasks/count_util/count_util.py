

def count_util(text: str, flags: str | None = None) -> dict[str, int]:
    """
    :param text: text to count entities
    :param flags: flags in command-like format - can be:
        * -m stands for counting characters
        * -l stands for counting lines
        * -L stands for getting length of the longest line
        * -w stands for counting words
    More than one flag can be passed at the same time, for example:
        * "-l -m"
        * "-lLw"
    Ommiting flags or passing empty string is equivalent to "-mlLw"
    :return: mapping from string keys to corresponding counter, where
    keys are selected according to the received flags:
        * "chars" - amount of characters
        * "lines" - amount of lines
        * "longest_line" - the longest line length
        * "words" - amount of words
    """
    flag_list = {'l': False, 'm': False, 'L': False, 'w': False}

    if flags is None or len(flags) == 0:
        flag_list = {'l': True, 'm': True, 'L': True, 'w': True}
    else:
        for flag in flags.split():
            for char in flag:
                if char in flag_list:
                    flag_list[char] = True
    answer = {}
    if flag_list['m']:
        answer['chars'] = len(text)
    if flag_list['l']:
        answer['lines'] = str.count(text, '\n')
    if flag_list['w']:
        answer['words'] = len(text.split())
    if flag_list['L']:
        answer['longest_line'] = max([len(line) for line in text.split('\n')])
    return answer


