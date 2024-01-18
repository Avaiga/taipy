import pickle
from Crypto.Cipher import AES
from base64 import b64encode, b64decode


__all__ = "encrypt", "decrypt"

BLOCK_SIZE = 16
INTERRUPT = b'\0'  # something impossible to put in a string
PADDING = b'\1'


def pad(data):
    return data + INTERRUPT + PADDING * (BLOCK_SIZE - (len(data) + 1) % BLOCK_SIZE)


def strip(data):
    return data.rstrip(PADDING).rstrip(INTERRUPT)


def create_cipher(key, seed):
    if len(seed) != 16:
        raise ValueError("Choose a seed of 16 bytes")
    if len(key) != 32:
        raise ValueError("Choose a key of 32 bytes")
    return AES.new(key, AES.MODE_CBC, seed)


def encrypt(plaintext_data, key, seed):
    plaintext_data = pickle.dumps(plaintext_data, pickle.HIGHEST_PROTOCOL)  # whatever you give me I need to be able to restitute it
    return b64encode(create_cipher(key, seed).encrypt(pad(plaintext_data)))


def decrypt(encrypted_data, key, seed):
    return pickle.loads(strip(create_cipher(key, seed).decrypt(b64decode(encrypted_data))))
