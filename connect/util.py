import random

from collections import namedtuple

banner = '''\nWelcome to connect, I hope you enjoy your dots.\n- Skyler Knecht[ka-ne-ct]\n'''
chars = ['a', 'b' 'c' 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
data = [
'''When you bring your best to the table, no matter where you are or what you are doing, you bring out the best in others. And soon, you start to realize, that, in turn, helps them bring out the best in you. That’s the upward spiral. You find each other and form an elite group of go-to people in an otherwise ordinary context. I see that happen everywhere I go: circles or networks of go-to people who help each other and go out of their way to be mutually reliable.''',
'''“My mother always wanted to live near the water," she said. "She said it's the one thing that brings us all together. That I can have my toe in the ocean off the coast of Maine, and a girl my age can have her toe in the ocean off the coast of Africa, and we would be touching. On opposite sides of the world.”''',
'''“Reconnect to what makes you happy and brings you Joy. If there is something that used to make you happy which you have stopped doing, do it again. Seek to find deeper meaning and significance rather than living on the surface.”'''
]
Function = namedtuple('Function', ['name', 'description', 'option_type', 'dependencies'])
headers = [
'''The connection flows through us all.''',
'''Connection of us flows through you.''',
'''Enjoyment is the best connection of all.'''
]
ids = []
MenuOption = namedtuple('MenuOption', ['function', 'description', 'category', 'color', 'arguments'])
ssl = False
strs = []
titles = ['The connections you build over time.', 'Everything is connected.', 'Unlock the mind to connect to the universe of thought.']
verbose = False
version = '0.0'

random_data=(titles[random.randint(0,len(titles)-1)], headers[random.randint(0,len(headers)-1)], data[random.randint(0,len(data)-1)])

def generate_id():
    new_id = [str(random.randint(0,9)) for random_integer in range (0,10)]
    new_id = ''.join(new_id)
    if new_id in ids:
        new_id = generate_id()
    ids.append(new_id)
    return new_id

def generate_str():
    new_str = [str(chars[random.randint(0, len(chars)-1)]) for random_char in range (0,10)]
    new_str = ''.join(new_str)
    if new_str in strs:
        new_str = generate_str()
    strs.append(new_str)
    return new_str

def server_context():
    if ssl:
        return 'https'
    return 'http'
