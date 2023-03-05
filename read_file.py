import io

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES

f = open("zed_is_dead.txt", "rb")
d1 = f.read()
print(len(d1))
f.close()

f = open("zed_is_dead.txt.aesd", "rb")
d2 = f.read()
print(len(d2))
f.close()

print(len(d2)-len(d1))
print('-'*72)

k1 = bytes.fromhex("210be6a9efacd891729588a1b56eb1b68f3fe6e9cb5283cdb459293c4d0146b4")
k2 = bytes.fromhex("da319cc5410ba8dc8edbfd184d26e371e5efb9d821750b99af3bac0eaf30c59d")

backend = default_backend()
algo1 = AES(k1)
algo2 = AES(k2)
cipher2 = Cipher(algo2, modes.ECB())

f = open("zed_is_dead.txt.aesd", "rb")
a = f.read(144)
while True:
    chunk = f.read(512)
    if chunk:
        tweak = bytes.fromhex("00"*16)
        enc2 = cipher2.encryptor()
        encrypted_tweak = enc2.update(tweak)
        # Ok jusqu'ici
        # ensuite on bidouille le tweak dans TweakCrypt
        mode1 = modes.XTS(encrypted_tweak)
        cipher1 = Cipher(algo1, mode1, backend)
        decrypted_chunk = cipher1.decryptor().update(chunk)
        print(chunk.hex())
        print(decrypted_chunk.decode())
        print('-'*72)
    else:
        break
f.close()


#Read
"""
4145534400000000000000008dd7fedd11544e72ba7a3699fa23dad270fc2c9fc91d8c760998bc400375456e8be3a38ec4c5ee587ea9268a893f151d99d1f62c
d789266cf7bc8261faf89e1863f6d847025380ec63c2a3e4546e3041c38a395422e572eb324367354804197991872870ab010cbabdda8bb42a107cf76a2a2891
145577c358c965480c4ec4c9ca9b48b950c623e7361bfbaaa3acd6177de3c0b958383577ad48997c0ddfc449e5b984b71a7f488a29dcb4de06c9d0eb3d81d441
40dd849dd946e1e18d86c648d73988e06a5d7a480d08d4f074efe578579672e1d77d353bd64dc1751bcd0a411c190bd312313d40c9b70224910a95de0feb5ae0
9dedf33499c9ff55e9a41017013a5fba89e3cffda6c429a92923e6d5296fd2349ebcc1ba4d009ccc76ca0afa24407c6843790e106720644074b634421c09878f
be9537375caf06fbb3226d75ea2222cce64eaffdc8bc7e24aded34368ec9bb4641b09896272f2a32fc540320fac5f9f60032885d61098321cadca903495722e8
cadd31c4c926db56af78ba66ab93016b00d4dd56a6333ad2bd6d5ec3924257ed0c094b91ff6c3d8298c309cb070540832f071f9cee2fe2682d3c91726bd2e7d1
40f987ec574995ef414e16e56a90c0eef96398f26887bf9a9a20693578041883518e54ae269348a36afd9297d2f996199ed52885bef231c28970b95e9471f2c0
"""

"""
Padding length............................. (3) 464
XTS AES key #1............................ (64) 210be6a9efacd891729588a1b56eb1b68f3fe6e9cb5283cdb459293c4d0146b4
XTS AES key #2............................ (64) da319cc5410ba8dc8edbfd184d26e371e5efb9d821750b99af3bac0eaf30c59d

1st tweak: 00 00 00 00 00 00 00... -> 3C 59 6E 1F 04 70 D9 A6...
2nd tweak: 01 00 00 00 00 00 00... -> DF AB 4B 9D 0D B7 C6 2D...

"""