import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


def create_key(password_provided):
    password = password_provided.encode() # convert to type bytes
    salt = b"\xc5\xb3[F\xa4\xe1\\\xe9\x82\xb2\x85@ee\xec'" # generated with os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(key, string):
    string = string.encode()
    f = Fernet(key)
    encryptedString = f.encrypt(string)
    return encryptedString


def decrypt(key, string):
    f = Fernet(key)
    decryptedString = f.decrypt(string)
    return decryptedString
