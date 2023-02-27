import os
import json
import base64
import binascii as ba


# =======================================================================================================================
#
#   Class for the encrypted file (your file, containing your datas)
#
# =======================================================================================================================

# Reference : https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat

#
# The data file also contains crypto information we need to gather. The file structure depends on the cipher blocksize,
# which is one of the information within the file.
#
# In the file structure, the first block is reserved for the boxcryptor header. This block size is calculated as
# 'offset', and it's padded with NUL (\x00)
#
# +-------------+-------------+-----------+----------------+----------------+-------...------------+
# | boxcryptor  | Json with   | Padding   | Encrypted      | Encrypted      |       ...            |
# | header      | crypto info | with \x00 | data block #1  | data block #2  |       ...            |
# | (48 bytes)  |             |           |                |                |       ...            |
# +-------------+-------------+-----------+----------------+----------------+-------...------------+
# |                                       |                |                |                      |
# |<------------------------------------->|<-------------->|<-------------->|                      |
# |                                       |   blocksize    |   blocksize    |                      |
# 0                                    offset                                                 filesize
#

class DataFile:

    def __init__(self, data_filepath):

        """
            The init function is the constructor. All we need is the file path.
            We assume that there is no syntax or structure error in the file

            The header is 144 bytes long. 
        """

        self.filepath = data_filepath
        d_file = open(data_filepath, 'rb')
        self.raw_header = d_file.read(144)

        # 1st, get the boxcryptor specific header (48 bytes)
        file_header = self.raw_header

        # Header parsing
        self.file_type             = file_header[0:4].decode("utf-8")
        self.file_type_version     = int(file_header[4])
        self.reserved_1            = int.from_bytes(file_header[5:11], byteorder='little')
        self.crc32_checksum        = int.from_bytes(file_header[12:15], byteorder='little')
        self.global_salt           = int.from_bytes(file_header[16:31], byteorder='little')
        self.file_salt             = int.from_bytes(file_header[32:47], byteorder='little')

        self.aes_gcm_header        = file_header[48:127]
        self.aes_gcm_auth_tag      = file_header[128:143]

        # The 32 last bytes may be hash value
        some_hash     = file_header[16:48]
        self.hash     = some_hash.hex()

        # JSON data (file content and encryption information)
        #crypto_json_txt  = d_file.read(self.header_core_length)
        crypto_json_txt  = self.raw[48:48+self.header_core_length]
        self.crypto_json = json.loads(crypto_json_txt)

        # JSON Parsing
        self.cipher_algo          = self.crypto_json["cipher"]["algorithm"]
        self.cipher_mode          = self.crypto_json["cipher"]["mode"]
        self.cipher_padding_mode  = self.crypto_json["cipher"]["padding"]
        self.cipher_keysize       = self.crypto_json["cipher"]["keySize"]
        self.cipher_blocksize     = self.crypto_json["cipher"]["blockSize"]
        self.cipher_iv            = base64.b64decode(self.crypto_json["cipher"]["iv"])

        efk                       = self.crypto_json["encryptedFileKeys"][0]
        self.file_type            = efk["type"]
        self.file_id              = efk["id"]
        self.file_size            = os.path.getsize(data_filepath)

        self.aes_key_encrypted_bytes = base64.b64decode(efk["value"])

        # EOF
        d_file.close()



#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
    

