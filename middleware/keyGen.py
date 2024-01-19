# Generate 256-bit key for AES encryption

from Crypto.Cipher import AES
from datetime import datetime

def generateKey():
    try:
        # Generate 256-bit key for AES encryption
        key = AES.get_random_bytes(16)

        # Write key to file
        f = open("./middleware/key/aes_key", "wb")
        f.write(key.hex().encode('utf-8'))
        f.close()

        return 1
    except Exception as e:
        f = open("logs/middleware.log", "a")
        f.write(f"[ERROR] {datetime.now()}: {e}\n")
        f.close()
        return -1
    
# print(generateKey())