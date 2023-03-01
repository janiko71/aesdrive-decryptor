#!/usr/bin/env python3
# ----------------------------------------------------------
#
#                   AES Drive Decryptor
#
# ----------------------------------------------------------

DEFAULT_FILE = "zed.txt.aesd"
#DEFAULT_FILE = "aes_drive_test.txt.aesd"
DEFAULT_FILE = "AESDrive_Settings.ini.aesd"

KDF_ITERATIONS = 50000
DEFAULT_PWD = "123456"

#
# This program is intended to decrypt a SINGLE encrypted file 
# from the AES Drive solution.
#

"""
    Standard packages
"""

import os
import sys
import pprint
import json
import base64
import binascii as ba
import getpass
import time
import hashlib

from colorama import Fore, Back, Style 


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

"""
    My packages
"""

import res.aesdatafile as aesdatafile
import res.fnhelper as helper



# ===========================================================================
#
#   main() program
#
# ===========================================================================


# -----------------------------------------------------------------
#
#  Reading arguments (in command line or in some configuration)
#
# -----------------------------------------------------------------


arguments = helper.check_arguments(sys.argv)

if (arguments == None):
    exit()



"""
    Reading data filepath
"""
if (arguments.get("file")):
    
    # Data filepath in commande line
    data_filepath = arguments.get("file")
    
else:
    
    # no => input()
    data_filepath = str(input("Data file: ") or DEFAULT_FILE)


"""
    Constructing output file name
"""
encrypted_data_filename, encrypted_data_fileext = os.path.splitext(data_filepath)
original_dir, original_file = os.path.split(data_filepath)


if (encrypted_data_fileext != ".aesd"):
    print("Error: the file you want to decrypt has a bad suffix (filename:" + encrypted_data_filename + ")")
    exit(1)
    
else:    
    new_filename = encrypted_data_filename

"""
    Reading data file itself
"""

if (os.path.isfile(data_filepath)):
    
    print("Decrypting \'" + data_filepath + "\' file...")
    data_file = aesdatafile.DataFile(data_filepath)
    
else:
    
    print("File \'" + data_filepath + "\' not found!")
    exit()

"""
    Reading user's password
"""
if (arguments.get("pwd")):
    
    # password in command line
    pwd = arguments.get("pwd")
    
else:
    
    # no => input()
    pwd = str(getpass.getpass(prompt="AES Drive password: ") or DEFAULT_PWD)


"""
    Printing files info
"""
print('-'*72)
helper.print_parameter("Data directory", os.path.abspath(original_dir))
helper.print_parameter("File name (input)", original_file)
helper.print_parameter("File name (output)", new_filename)
helper.print_data_file_info(data_file)
 


# -----------------------------------------------------------------
#
#  Constructing crypto elements
#
# -----------------------------------------------------------------

"""
    Crypto init
"""    
backend   = default_backend()


#
# Public key
# ===============
#
# RSA-4096 key is in DER format
# 738 base64 (6-bits) = 123 bytes
#

#public_key = serialization.load_der_public_key(
#    keyfile.public_key_bytes,
#    backend
#)
#helper.print_parameter("Public key importation", "OK")


#
# Password key
# =================
#
# --> Password key: A "double" AES encryption key derived from your password. The key is created using the key stretching and
#     strengthening function PBKDF2 with HMACSHA512, 10.000 iterations and a 24 byte salt.
#
#     The password key is used to encrypt the user's private key.
#
#     The salt is base64-encode
#     The password should be unicode (UTF8) encoded
#

"""
    Derivation of the user's password
"""
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=data_file.global_salt,
    iterations=KDF_ITERATIONS,
    backend=backend
)

pwd_derived_key = kdf.derive(pwd.encode())
pwd = None
helper.print_parameter("Password derived key creation", "OK")
helper.print_parameter("Derived key", pwd_derived_key.hex())

file_seed = pwd_derived_key + data_file.file_salt
helper.print_parameter("File seed", file_seed.hex())

sha512 = hashlib.sha512()
sha512.update(file_seed)
file_key_hash = sha512.digest()
helper.print_parameter("Key hash computed", "OK")
helper.print_parameter("File key hash", file_key_hash.hex())

header_encryption_key = file_key_hash[0:32]
init_vector           = file_key_hash[32:44]
helper.print_parameter("Header encr. key", header_encryption_key.hex())
helper.print_parameter("Init vector", init_vector.hex())

helper.print_parameter("Private key and init vector computed", "OK")


#
# --> Now we have to decrypt the header [48:127].
#
# file_aes_key_encrypted is the AES key encrypted with the user's public key
#
aesgcm = AESGCM(header_encryption_key)

decrypted_header = aesgcm.decrypt(init_vector, data_file.aes_gcm_header, data_file.aes_gcm_auth_tag)

the_file_aes_key = the_private_key.decrypt(
    data_file.aes_key_encrypted_bytes,
    asymmetric.padding.OAEP(
        mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA1(),
        label=None
    )
)
helper.print_parameter("AES file key decryption", "OK")
crypto_key = the_file_aes_key[32:64]
#print_parameter("AES file key", crypto_key.hex()) ==> only if you want it
print('-'*72)




# -----------------------------------------------------------------
#
#  Data file decryption
#
# -----------------------------------------------------------------

#
# Decrypt the encrypted file key using the user’s private key. Decrypt the encrypted data using the file key.
#
#      - Algo AES with a key length of 256 bits,
#      - Mode CBC (Cipher Block Chaining)
#      - Padding PKCS7
#

"""
    Let's calculate the nb of blocks to decrypt. All block are 'data_file.cipher_blocksize', except the last
    which can be shorter, but with cryptography.io module, the padding is automatically done.
"""
offset = 48 + data_file.header_core_length + data_file.header_padding_length
encrypted_data_length = data_file.file_size - offset - data_file.cipher_padding_length
nb_blocks = encrypted_data_length // data_file.cipher_blocksize
if ((encrypted_data_length % data_file.cipher_blocksize) != 0):
    nb_blocks += 1

helper.print_parameter("Encrypted data length", encrypted_data_length)
helper.print_parameter("Offset", offset)
helper.print_parameter("Number of blocks to decrypt", nb_blocks)
print()
print("="*72)
print("Start decrypting...")
print("-"*72)
print()

"""
    Execution time, for information
"""    
t0 = time.time()

"""
    Decrypts all the blocks
"""
f_in  = open(data_filepath, "rb")
f_out = open(new_filename, "wb")   # Yes, we overwrite the output file

# Read the 1st block (header), not used here
f_in.read(offset)

# Now read all the encrypted blocks
for block_nb in range (1, nb_blocks + 1):
    
    block_range = block_nb * data_file.cipher_blocksize
    #block = data_file.raw[block_range:block_range + data_file.cipher_blocksize]
    block = f_in.read(data_file.cipher_blocksize)
    block_length = len(block)
    
    # Compute block IV, derived from IV
    block_iv = helper.compute_block_iv(data_file.cipher_iv, block_nb - 1, crypto_key, backend)

    # Setting parameters for AES decryption (the key and the init vector)
    cipher = Cipher(algorithms.AES(crypto_key), modes.CBC(block_iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_block = decryptor.update(block)
    decryptor.finalize()

    # Padding exception for the last block
    progression = (block_nb / nb_blocks * 100)
    print("Fileblock #{}, progression {:6.2f} %".format(block_nb, progression), end="\r", flush=True)
    if (block_nb == nb_blocks):
        decrypted_block = decrypted_block[:-data_file.cipher_padding_length]
    f_out.write(decrypted_block)

f_in.close
f_out.close()

"""
    Execution time, for information
"""    
execution_time = time.time() - t0

print("{} blocks decrypted in {:.2f} seconds".format(nb_blocks, execution_time))

print()
print("-"*72)
print("End of decrypting...")
print("="*72)


#
# Notes:
#
# --> AES keys (encrypted with the user's password / wrapping key)
#
# --> Wrapping key: This key is the root AES key which is used to encrypt all other AES keys stored on our servers.
#
# --> Filename key: This key is used to encrypt filenames if filename encryption is enabled.
