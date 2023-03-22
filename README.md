# aesdrive-decryptor
1st try to check the crypto part of the AES Drive from /n Software.

In progress.

1. Header decryption: done
1. XTS-AES: DONE with standard Python libraries (cryptography). That means that the algo seems to be used correctly by /n software in this product.
1. Check the secret generation => OK (they use .NET crypto functions)
