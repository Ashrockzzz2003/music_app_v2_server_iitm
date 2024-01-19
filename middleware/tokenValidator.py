from Crypto.Cipher import AES

from datetime import datetime

def validateToken(token, nonce, tag):
    try:
        # Check if token is a string
        if type(token) != str:
            # print("[ERROR]: Token is not a string!")
            return -1
        
        # Read key from file
        f = open("./middleware/key/aes_key", "rb")
        key = f.read()
        f.close()

        # Generate cipher
        cipher = AES.new(key, AES.MODE_EAX, nonce=bytes.fromhex(nonce))

        # Decrypt token
        decryptedToken = cipher.decrypt_and_verify(bytes.fromhex(token), bytes.fromhex(tag)).decode('utf-8')

        decryptedToken = eval(decryptedToken)

        # Check if token is expired
        if datetime.strptime(decryptedToken['expires_at'], "%d-%m-%Y %H:%M:%S") < datetime.now():
            # print("[ERROR]: Token is expired!")
            return -2

        return decryptedToken
    except Exception as e:
        # print("[ERROR]: Could not validate token!")
        return -1


# print(validateToken('1fad1426bc3e83056b36002a6b1ffd07a253b1f75be384b99c8a537edda5342f1a54c13c2a81efce32baaa1f8593191459770dfd4533e278a96422', '345d81f6352d1c696f43f183e55e3492', '1ae46fd2a696cc3c9e57bc0924dec2b2'))