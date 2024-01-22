import re


def validateEmail(userEmail):
    # Regular userEmail Address Regex
    emailRegex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(emailRegex, userEmail) and len(userEmail) <= 255:
        return True
    return False


def validatePassword(userPassword):
    if len(userPassword) >= 8 and len(userPassword) <= 255:
        return True

    return False
