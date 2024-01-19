from Crypto.Cipher import AES
from datetime import datetime, timedelta

def generateToken(payLoad):
    try:
        # Check if payLoad is JSON
        if type(payLoad) != dict:
            print("[ERROR]: Payload is not JSON!")
            return -1

        payLoad['expires_at'] = (datetime.now() + timedelta(minutes=120)).strftime("%d-%m-%Y %H:%M:%S")

        # Read key from file
        f = open("./middleware/key/aes_key", "rb")
        key = f.read()
        f.close()

        # Generate cipher
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce

        # Encrypt payLoad
        cipherText, tag = cipher.encrypt_and_digest(str(payLoad).encode('utf-8'))

        return f"{cipherText.hex()},{nonce.hex()},{tag.hex()}"
        
    except Exception as e:
        f = open("./logs/middleware.log", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        return -1
    
# print(generateToken({'userName': 'Ashwin'}))