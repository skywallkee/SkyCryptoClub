# STRING
import string

# RANDOM
import random

def get_json_data(body, params):
    result = []
    for param in params:
        if param in body:
            result.append(body[param])
    return result

def generate_password():
    characters = string.ascii_letters + string.digits
    stringLength = 20
    return ''.join(random.choice(characters) for i in range(stringLength)).replace(" ", "")

