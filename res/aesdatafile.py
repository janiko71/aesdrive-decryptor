import os, sys
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

        # Raw Header
        file_header = self.raw_header

        # Header parsing
        self.file_type             = file_header[0:4].decode("utf-8")
        self.file_type_version     = int(file_header[4])
        self.reserved_1            = file_header[5:12]
        self.crc32_checksum        = ba.hexlify(file_header[12:16])
        self.global_salt           = file_header[16:32]
        self.file_salt             = file_header[32:48]

        self.aes_gcm_header        = file_header[48:128]
        self.aes_gcm_auth_tag      = file_header[128:144]

        # Checksum
        header_copy = file_header[0:12] + b'\x00\x00\x00\x00' + file_header[16:144]
        h = ba.crc32(header_copy)
        h_ctrl = ba.hexlify(h.to_bytes(4, 'big'))

        # h_ctrl and self.crc32_checksum should be the same
        if (h_ctrl != self.crc32_checksum):
            print("Checksum error")
            sys.exit(0)


        # EOF
        d_file.close()



#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
    

