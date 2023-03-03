import os

"""
    Crypto packages
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
    My values (in hex format):

    encryption key:9152c772b80924a10c1301c467a38f46ba7f43fe4b8a96dbcc56d405ca44cc1b
    init-vector:'a90a571211ee38f00e29a7a8a92fffe5'
    aes_gcm_header:'a5f877b9152b5c2d79625bf55a165d577410e513aee229468410a96aec98e649348fb5784331544ff7a4003600844d5bd5c5cd298943e32b18f7b7044a776c396e493d5de7852d19ebbd3b539f7e044a'
    aes_gcm_auth_tag:ad380d31108e9a1751b87821cbb598c8

    Your values:

    encryption key:9152C772B80924A10C1301C467A38F46BA7F43FE4B8A96DBCC56D405CA44CC1B
    init-vector:A90A571211EE38F00E29A7A8A92FFFE5
    aes_gcm_header:A5F877B9152B5C2D79625BF55A165D577410E513AEE229468410A96AEC98E649348FB5784331544FF7A4003600844D5BD5C5CD298943E32B18F7B7044A776C396E493D5DE7852D19EBBD3B539F7E044A
    aes_gcm_auth_tag:AD380D31108E9A1751B87821CBB598C8
"""

key64 = bytes.fromhex('9152c772b80924a10c1301c467a38f46ba7f43fe4b8a96dbcc56d405ca44cc1b')
iv16 = bytes.fromhex('a90a571211ee38f00e29a7a8a92fffe5')
iv12 = bytes.fromhex('a90a571211ee38f00e29a7a8a92fffe5')
encrypted_msg = bytes.fromhex('a5f877b9152b5c2d79625bf55a165d577410e513aee229468410a96aec98e649348fb5784331544ff7a4003600844d5bd5c5cd298943e32b18f7b7044a776c396e493d5de7852d19ebbd3b539f7e044a')
auth_tag = bytes.fromhex('ad380d31108e9a1751b87821cbb598c8')

aesgcm = AESGCM(key64)

print("iv12        ", len(iv12), iv12.hex())
print("iv16        ", len(iv16), iv16.hex())
print("key64       ", len(key64), key64.hex())
print("auth_tag    ", len(auth_tag), auth_tag.hex())
print("encrypted   ", len(encrypted_msg), encrypted_msg.hex())

try:
    res = aesgcm.decrypt(iv12, encrypted_msg, auth_tag)
    print(res.encode())
except Exception as e:
    print(f"Bad with 12-bytes ({type(e)})")

try:
    res = aesgcm.decrypt(iv12, encrypted_msg, None)
    print(res.encode())
except Exception as e:
    print(f"Bad with 12-bytes and no auth_tag ({type(e)})")

try:
    res = aesgcm.decrypt(iv16, encrypted_msg, auth_tag)
    print(res.encode())
except Exception as e:
    print(f"Bad with 16-bytes ({type(e)})")

try:
    res = aesgcm.decrypt(iv16, encrypted_msg, None)
    print(res.encode())
except Exception as e:
    print(f"Bad with 16-bytes and no auth_tag ({type(e)})")

try:
    msg = encrypted_msg + auth_tag
    res = aesgcm.decrypt(iv12, msg, None)
    print(res.encode())
except Exception as e:
    print(f"Bad with 12-bytes concatenated auth_tag ({type(e)})")