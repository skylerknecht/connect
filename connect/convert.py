import base64
import collections
import random

def base64_to_bytes(data) -> bytes:
    """
    Base64 encode a bytes object.
    :param data: A base64 string.
    :return: A bytes object.
    :rtype: bytes
    """
    return base64.b64decode(data)


def base64_to_string(data) -> str:
    """
    Base64 decode a string.
    :param data: A base64 string.
    :return: A base64 decoded string
    :rtype: str
    """
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')


def bytes_to_base64(data) -> str:
    """
    Base64 encode a bytes object.
    :param data: A python bytes object.
    :return: A base64 encoded string
    :rtype: str
    """
    return base64.b64encode(data).decode('utf-8')


def string_to_base64(data) -> str:
    """
    Base64 encode a string.
    :param data: A python string.
    :return: A base64 encoded string
    :rtype: str
    """
    return str(base64.b64encode(data.encode()), 'utf-8')

def xor_base64(data):
    """
    Encrypt data using the XOR algorithm and return a Base64 string
    of the encrypted data. This function is used for light obfuscation
    for arguments to agents. The key is a randomly generated integer
    from 0 to 255.
    :param bytes data: The data to encrypt.
    :return: The key used for XOR encryption.
    :return: The base64 encoded string of the XOR encryption.
    :rtype: tuple
    """
    key = random.randint(0, 255)
    encoded_data = collections.deque()
    for byte in data:
        e_byte = (byte ^ key)
        encoded_data.append(e_byte)
    return bytes_to_base64(bytes(encoded_data)), str(key)