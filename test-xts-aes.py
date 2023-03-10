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
from cryptography.hazmat.primitives.ciphers.algorithms import AES

def xor16(bytes1, bytes2):

    res = bytes([a ^ b for a,b in zip(bytes1, bytes2)])
    return res

"""
    k1:              '0496801a02924a07f0cd10ce6ead6b64c1de4379b61772faf73432991f3d42f4'
    k2:              'f79314e28ce4a060bb305ea7c4518f3a6ac0f03acc3d0ba730a5b2307ce1f59b'
    tweak:           '00000000000000000000000000000000'
    encrypted_tweak: 'e9edcd08a842eff8303058ff57105561'

    chunk:           '50c623e7361bfbaaa3acd6177de3c0b958383577ad48997c0ddfc449e5b984b71a7f488a29dcb4de06c9d0eb3d81d44140dd849dd946e1e18d86c648d73988e06a5d7a480d08d4f074efe578579672e1d77d353bd64dc1751bcd0a411c190bd312313d40c9b70224910a95de0feb5ae09dedf33499c9ff55e9a41017013a5fba89e3cffda6c429a92923e6d5296fd2349ebcc1ba4d009ccc76ca0afa24407c6843790e106720644074b634421c09878fbe9537375caf06fbb3226d75ea2222cce64eaffdc8bc7e24aded34368ec9bb4641b09896272f2a32fc540320fac5f9f60032885d61098321cadca903495722e8cadd31c4c926db56af78ba66ab93016b00d4dd56a6333ad2bd6d5ec3924257ed0c094b91ff6c3d8298c309cb070540832f071f9cee2fe2682d3c91726bd2e7d140f987ec574995ef414e16e56a90c0eef96398f26887bf9a9a20693578041883518e54ae269348a36afd9297d2f996199ed52885bef231c28970b95e9471f2c02f9aba5c53e71d382bbc81df3eb58f5f5e738d1d840527a5c46ab6ee61d9fc4bcfb959e9986894dbd32711788e8fe81915e835f20b97fd0c3d97c95cfb27d5636b05c1ea174ddde977da263590f75058c96129e1e5e13a7bd8e0a86e7e6e79de30bbd6b13c2ecb1e73a3362ea0f60b23bd52cabec87c6964249be67157b899d0570987f3b917722a39f5f87fcdb580ec'
    attendu:         '4465732064c3a96368657473206a6f6e6368616e74206c657320727565732c20646573207a6f6d626965732073e2809961676974616e74206175206d696c6965...'
"""


k1              = bytes.fromhex('0496801a02924a07f0cd10ce6ead6b64c1de4379b61772faf73432991f3d42f4')
k2              = bytes.fromhex('f79314e28ce4a060bb305ea7c4518f3a6ac0f03acc3d0ba730a5b2307ce1f59b')
double_key      = k1 + k2
tweak           = bytes.fromhex('00000000000000000000000000000000')
encrypted_tweak = bytes.fromhex('e9edcd08a842eff8303058ff57105561')

chunk           = bytes.fromhex('50c623e7361bfbaaa3acd6177de3c0b958383577ad48997c0ddfc449e5b984b71a7f488a29dcb4de06c9d0eb3d81d44140dd849dd946e1e18d86c648d73988e06a5d7a480d08d4f074efe578579672e1d77d353bd64dc1751bcd0a411c190bd312313d40c9b70224910a95de0feb5ae09dedf33499c9ff55e9a41017013a5fba89e3cffda6c429a92923e6d5296fd2349ebcc1ba4d009ccc76ca0afa24407c6843790e106720644074b634421c09878fbe9537375caf06fbb3226d75ea2222cce64eaffdc8bc7e24aded34368ec9bb4641b09896272f2a32fc540320fac5f9f60032885d61098321cadca903495722e8cadd31c4c926db56af78ba66ab93016b00d4dd56a6333ad2bd6d5ec3924257ed0c094b91ff6c3d8298c309cb070540832f071f9cee2fe2682d3c91726bd2e7d140f987ec574995ef414e16e56a90c0eef96398f26887bf9a9a20693578041883518e54ae269348a36afd9297d2f996199ed52885bef231c28970b95e9471f2c02f9aba5c53e71d382bbc81df3eb58f5f5e738d1d840527a5c46ab6ee61d9fc4bcfb959e9986894dbd32711788e8fe81915e835f20b97fd0c3d97c95cfb27d5636b05c1ea174ddde977da263590f75058c96129e1e5e13a7bd8e0a86e7e6e79de30bbd6b13c2ecb1e73a3362ea0f60b23bd52cabec87c6964249be67157b899d0570987f3b917722a39f5f87fcdb580ec')
chunk128        = chunk[0:128]

algo = AES(double_key)
mode = modes.XTS(tweak)
cipher = Cipher(algo, mode)

decryptor = cipher.decryptor()
res = decryptor.update(chunk)

print(res.hex())
print(res.decode())

