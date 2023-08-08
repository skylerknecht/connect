import os
import random

from hashlib import md5

alphabet = []
endpoints = []
firstnames = []
lastnames = []

with open(f'{os.getcwd()}/resources/alphabet.txt', 'r') as _alphabet:
    for character in _alphabet:
        alphabet.append(character)

with open(f'{os.getcwd()}/resources/firstnames.txt', 'r') as _firstnames:
    for firstname in _firstnames:
        firstnames.append(firstname)

with open(f'{os.getcwd()}/resources/lastnames.txt', 'r') as _lastnames:
    for lastname in _lastnames:
        lastnames.append(lastname)


def digit_identifier(length: int = 10) -> str:
    """
    Generate random integers from 1 to 9 and concatenate the digits
    together for a length of zero to *length*.
    
    :param: int length: The amount of random digits to concatenate.
    :return: The generated digit identifier.
    :rtype: str
    """
    _identifier = [str(random.randint(1, 9)) for _ in range(0, length)]
    _identifier = ''.join(_identifier)
    return _identifier


def name_identifier() -> str:
    """
    Generate a random name in the format firstname lastname.
    :return: The generated name identifier.
    :rtype: str
    """
    _firstname = firstnames[random.randint(0, len(firstnames) - 1)].rstrip().capitalize()
    _lastname = lastnames[random.randint(0, len(lastnames) - 1)].rstrip().capitalize()
    return f'{_firstname} {_lastname}'


def string_identifier(length: int = 10) -> str:
    """
    Generate random upper and lowercase characters and concatenate
    them for a length of zero to *length*.
    :param: int length: The amount of random characters to concatenate.
    :return: The generated string identifier.
    :rtype: str
    """
    _identifier = [alphabet[random.randint(0, len(alphabet) - 1)].rstrip() for _ in range(0, length)]
    _identifier = ''.join(_identifier)
    return _identifier


def md5_hash(path: str) -> str:
    _hash = md5()
    with open(path, 'rb') as fd:
        for chunk in iter(lambda: fd.read(4096), b''):
            _hash.update(chunk)
    return _hash.hexdigest()
