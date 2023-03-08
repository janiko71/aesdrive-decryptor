#!/usr/bin/env python3
# ----------------------------------------------------------
#
#                   AES Drive Decryptor
#
# ----------------------------------------------------------

DEFAULT_FILE = "aes_drive_test.txt.aesd"
DEFAULT_FILE = "test.png.aesd"
DEFAULT_FILE = "zed.txt.aesd"
DEFAULT_FILE = "zed_is_dead.txt.aesd"
DEFAULT_FILE = "lulu.jpg.aesd"

KDF_ITERATIONS = 50000
DEFAULT_PWD = "aesdformatguide"
PWD_ENCODING = "UTF8"
HEADER_LENGTH = 144
SECTOR_LENGTH = 512

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
import hashlib, hmac

from res.fnhelper import xor16, multiplyX

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
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from cryptography.exceptions import InvalidTag

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

    f_in  = open(data_filepath, "rb")
    file_header = f_in.read(HEADER_LENGTH)
    
    print("Decrypting \'" + data_filepath + "\' file...")
    data_file = aesdatafile.DataFile(file_header)
    file_stats = os.stat(data_filepath)
    
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

"""
    Derivation of the user's password
"""
kdf_v = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=data_file.global_salt,
    iterations=KDF_ITERATIONS,
    backend=backend
)

pwd_derived_key_verif = kdf_v.derive(pwd.encode(PWD_ENCODING))
pwd_derived_key = hashlib.pbkdf2_hmac("sha512", pwd.encode(PWD_ENCODING), data_file.global_salt, KDF_ITERATIONS, 32)

# Reset variable
pwd = None

helper.print_parameter("Password derived key creation", "OK")
helper.print_parameter("Derived key", pwd_derived_key.hex())
helper.print_parameter("Derived key verification", pwd_derived_key_verif.hex() + " (" + str(pwd_derived_key == pwd_derived_key_verif) + ")")

file_seed = pwd_derived_key + data_file.file_salt
# Error in doc! The salt is BEFORE the derived key!
file_seed = data_file.file_salt + pwd_derived_key
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
helper.print_parameter("Auth tag", data_file.aes_gcm_auth_tag.hex())

helper.print_parameter("Private key and init vector computed", "OK")


#
# --> Now we have to decrypt the header [48:127].
#

aesgcm = AESGCM(header_encryption_key)

# header and auth_tag should be concatenated here (--> /n software support)

encrypted_msg = data_file.aes_gcm_header + data_file.aes_gcm_auth_tag

try:
    decrypted_header = aesgcm.decrypt(init_vector, encrypted_msg, None)
except InvalidTag:
    helper.print_parameter("Decrypted header", helper.TERM_RED + helper.TERM_BOLD + "Error (InvalidTag), maybe wrong password?" + helper.TERM_RESET)
    exit(0)
except Exception as a:
    print("Very bad exception, should not happen ({})".format(e))
    exit(0)

helper.print_parameter("Decrypted header", decrypted_header.hex())

print('-'*72)

#
# --> Now analying the header
#

header_padding_length = int.from_bytes(decrypted_header[0:2], 'big')
header_reserved_1     = decrypted_header[2:16]
header_xts_key1       = decrypted_header[16:48]
header_xts_key2       = decrypted_header[48:80]

helper.print_parameter("Padding length", header_padding_length)
helper.print_parameter("XTS AES key #1", header_xts_key1.hex())
helper.print_parameter("XTS AES key #2", header_xts_key2.hex())

file_length = file_stats.st_size - HEADER_LENGTH - header_padding_length
helper.print_parameter("Expected data length", file_length)

print("-"*72)
print()

# -----------------------------------------------------------------
#
#  Data file decryption (with the XTS-AES key)
#
# -----------------------------------------------------------------

#
#  Algo: AES
#  Mode: XTS (https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.modes.XTS)
#  Block size: 512 bytes
#
#  Data is padded with 0x00 if needed (cf. padding_length)
#

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

f_out = open(new_filename, "wb")   # Yes, we overwrite the output file

backend = default_backend()

algo_key1 = AES(header_xts_key1)
algo_key2 = AES(header_xts_key2)

cipher_key1 = Cipher(algo_key1, modes.ECB())
cipher_key2 = Cipher(algo_key2, modes.ECB())

decryptor_key1 = cipher_key1.decryptor()
encryptor_key2 = cipher_key2.encryptor()

# Remember: we already read the first 144 bytes!

current_sector_offset = 0
byte_offset = 0
decrypted = ""

while True:

    chunk = f_in.read(SECTOR_LENGTH)
    len_chunk = len(chunk)
    tweak = current_sector_offset.to_bytes(16, 'little')
    encrypted_tweak = encryptor_key2.update(tweak)

    if chunk:
        
        for pos in range(0, len_chunk, 16):

            byte_offset = byte_offset + 16
            
            bytes_chunk = xor16(chunk[pos:pos+16], encrypted_tweak)
            decrypted_chunk = decryptor_key1.update(bytes_chunk)
            bytes_decrypted = xor16(decrypted_chunk, encrypted_tweak)
            #print(decrypt1.hex())
            #print(current_sector_offset, pos, bytes_decrypted.decode())

            if (byte_offset > file_length):
                # End of data!
                last_block_length = file_length % 16
                f_out.write(bytes_decrypted[0:last_block_length])
            else:
                f_out.write(bytes_decrypted)
            #print('-'*72)

            encrypted_tweak = multiplyX(encrypted_tweak)


        # Next sector
        current_sector_offset = current_sector_offset + 1 

    else:
        break

# EOF *2
# -----

f_in.close()
f_out.close()

print(decrypted)
print('-'*72)


"""
    Execution time, for information
"""    
execution_time = time.time() - t0

print("File decrypted in {:.2f} seconds".format(execution_time))

print()
print("-"*72)
print("End of decrypting...")
print("="*72)
