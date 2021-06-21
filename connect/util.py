import random

ids = []

def generate_id():
    new_id = [str(random.randint(0,9)) for random_integer in range (0,10)]
    new_id = ''.join(new_id)
    if new_id in ids:
        new_id = generate_id()
    ids.append(new_id)
    return new_id
