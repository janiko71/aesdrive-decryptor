# aesdrive-decryptor
1st try to check the crypto part of the AES Drive from /n Software.

In progress.

1. Header decryption: done
1. XTS-AES:
    1. Tweak encrypted: ok with key2
    1. XOR sur entrée avec tweak encrypted
    1. Déchiffrement bloc avec k1
    1. XOR avec tweak encrypted (encore)
    1. "Multiply"
