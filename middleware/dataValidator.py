import re


def validateEmail(userEmail):
    # Regular userEmail Address Regex
    if type(userEmail) != str:
        return False

    emailRegex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(emailRegex, userEmail) and len(userEmail) <= 255:
        return True
    return False


def validatePassword(userPassword):
    if type(userPassword) != str:
        return False

    if len(userPassword) >= 8 and len(userPassword) <= 255:
        return True

    return False

def validateUserFullName(userFullName):
    if type(userFullName) != str:
        return False

    fullNameRegex = r"^[a-zA-Z\s]*$"
    if re.fullmatch(fullNameRegex, userFullName) and len(userFullName) <= 255 and len(userFullName) >= 1:
        return True
    return False

def validateUserDob(userDob):
    if type(userDob) != str:
        return False

    dobRegex = r"^\d{4}-\d{2}-\d{2}$" # YYYY-MM-DD
    if re.fullmatch(dobRegex, userDob):
        return True
    return False

def validateGender(userGender):
    if type(userGender) != str:
        return False

    if userGender in ['M', 'F', 'O']:
        return True
    return False

def validateOtp(otp):
    if type(otp) != str:
        return False

    otpRegex = r"^\d{6}$"
    if re.fullmatch(otpRegex, otp):
        return True
    
    return False


def validateNonEmptyString(inputString):
    if type(inputString) != str:
        return False

    if len(inputString) > 0:
        return True

    return False


def isValidLoginToken(token):
    if "userId" in token and "userAccountStatus" in token and "userRoleId" in token and type(token["userId"]) == int and type(token["userAccountStatus"]) == str and type(token["userRoleId"]) == int and token["userAccountStatus"] == '1':
        return True

    
    return False

