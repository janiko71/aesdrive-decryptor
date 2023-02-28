import os

"""
    Crypto packages
"""

from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import keywrap
from cryptography.hazmat.primitives import asymmetric

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


key64 = AESGCM.generate_key(128)
iv = os.urandom(12)
msg_chiffre = "Message chiffré et hop !".encode()
auth_token  = "Token #01".encode()

aesgcm = AESGCM(key64)
encrypted = aesgcm.encrypt(iv, msg_chiffre, auth_token)

print("iv          ", iv.hex())
print("key64       ", key64.hex())
print("encrypted", len(encrypted), encrypted.hex())

"""
    iv           261d171edb117a5ce41d629f
    key64        1e4fd6c385c5dc6565da97c1f80459f7
    encrypted 41 17a564e0357457eeb0edd93b31ea465e984eab963bc079ea6415a21036c592732bcecb5a1a9be365f3
"""

print(aesgcm.decrypt(iv, encrypted, auth_token).decode())