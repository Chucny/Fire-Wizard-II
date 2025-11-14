import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def login(accounts_json):
    username = input("Enter username: ")

    if username not in accounts_json["users"]:
        return False

    password = input("Enter password: ")

    user_record = accounts_json["users"][username]
    salt = base64.b64decode(user_record["salt"])
    encrypted = user_record["encrypted"].encode()

    key = derive_key(password, salt)
    f = Fernet(key)

    try:
        decrypted = f.decrypt(encrypted).decode()
        if decrypted == username:
            return username
    except:
        pass

    return False
