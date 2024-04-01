import string
import secrets

def generate_otp():
    return "".join(secrets.choice(string.digits) for i in range(6))