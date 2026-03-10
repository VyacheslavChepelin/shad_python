
# alphabet = "abcdefghijklmnopqrstuvwxyz" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    dict = {}
    for index in range(26):
        dict[chr(ord('a') + index)] = chr((index + n) % 26 + ord('a'))
        dict[chr(ord("A") + index)] = chr((index + n) % 26 + ord("A"))
    return message.translate(str.maketrans(dict))
