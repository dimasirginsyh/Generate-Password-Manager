import secrets
import string


def password_generator(digit):
    special = '!@#$%^&*()-+?_=,<>/"'
    alphabet = string.ascii_letters + string.digits + special
    password = ''.join(secrets.choice(alphabet) for i in range(digit))
    return password
