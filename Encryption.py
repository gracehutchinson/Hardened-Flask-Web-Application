from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import base64
import os

class Encryption:
    def __init__(self):
        # key file so both init_db & app.py use the same encryption key
        self.key_file = 'secret.key'
        self.key = self.load_or_create_key()

    def load_or_create_key(self):
        # check if key already exists, if not make a new random one and save it
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = os.urandom(16)    # 128-bit key for aes
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt(self, raw):
        # don't try to encrypt empty stuff
        if not raw:
            return ""
        raw = raw.encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC)    # cbc mode gives us a random iv each time
        ct_bytes = cipher.encrypt(pad(raw, AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        # store IV and ciphertext together separated by so we can decrypt later
        return iv + ':' + ct

    def decrypt(self, enc):
        # if nothing/bad format just return as-is
        if not enc or ':' not in enc:
            return enc
        try:
            iv_str, ct_str = enc.split(':', 1)
            iv = base64.b64decode(iv_str)
            ct = base64.b64decode(ct_str)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8')
        except Exception as e:
            # if anything goes wrong show an error
            return "Error Decrypting"