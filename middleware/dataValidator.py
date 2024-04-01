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

def validateUserFullName(userFullName):
    fullNameRegex = r"^[a-zA-Z\s]*$"
    if re.fullmatch(fullNameRegex, userFullName) and len(userFullName) <= 255 and len(userFullName) >= 1:
        return True
    return False

def validateUserDob(userDob):
    dobRegex = r"^\d{4}-\d{2}-\d{2}$" # YYYY-MM-DD
    if re.fullmatch(dobRegex, userDob):
        return True
    return False

def validateGender(userGender):
    if userGender in ['M', 'F', 'O']:
        return True
    return False

def validateOtp(otp):
    otpRegex = r"^\d{6}$"
    if re.fullmatch(otpRegex, otp):
        return True
    
    return False

