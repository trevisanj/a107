import os
import random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

__all__ = ["encrypt_file", "decrypt_file", "get_key"]


def encrypt_file(key, filename_in, filename_out):
    chunk_size = 64*1024
    file_size = bytes("{:016}".format(os.path.getsize(filename_in)), "ASCII")
    # input vector

    iv = bytes(bytearray((random.randint(0, 0xFF) for _ in range(16))))

    encryptor = AES.new(key, AES.MODE_CBC, iv)

    with open(filename_in, "rb") as infile:
        with open(filename_out, "wb") as outfile:
            outfile.write(file_size)
            outfile.write(iv)

            while True:
                chunk = infile.read(chunk_size)

                n = len(chunk)
                if n == 0:
                    break
                elif n % 16 != 0:
                    chunk += b" " * (16 - n % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, filename_in, filename_out):
    chunk_size = 64*1024

    with open(filename_in, "rb") as infile:
        file_size = int(infile.read(16))
        iv = infile.read(16)

        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(filename_out, "wb") as outfile:
            while True:
                chunk = infile.read(chunk_size)

                if len(chunk) == 0:
                    break

                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(file_size)


def get_key(password):
    if isinstance(password, str):
        password = bytes(password, "UTF8")
    hasher = SHA256.new(password)
    return hasher.digest()
