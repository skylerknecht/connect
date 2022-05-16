import os
import random

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

with open(f'{os.getcwd()}/resources/endpoints.txt', 'r') as _endpoints:
    for endpoint in _endpoints:
        endpoints.append(endpoint)


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


def generate_endpoints(length: int = 10) -> str:
    """
    Generate a list of endpoints for stagers.

    :param length:
    :return:
    """
    return ','.join([endpoints[random.randint(0, len(endpoints) - 1)].rstrip() for _ in range(0, length)])


def generate_jitter(minimum: int = 1, maximum: int = 20) -> str:
    """
    Generate a random jitter between 1% and 20% for stagers.

    :param maximum:
    :param minimum:
    :return:
    """
    return str(float(random.randint(minimum, maximum)))


def generate_sleep(minimum: int = 5, maximum: int = 10) -> str:
    """
    Generate a random sleep between 5 and 10 for stagers.

    :param maximum:
    :param minimum: T
    :return:
    """
    return str(float(random.randint(minimum, maximum)))

