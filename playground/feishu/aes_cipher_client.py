import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from config.config import FEISHU_DATA


class AESCipher:
    def __init__(self, key=FEISHU_DATA.get('encrypt_key')):
        self.bs = AES.block_size
        # 使用 sha256 处理密钥，确保加密和解密时使用相同的密钥散列
        self.key = hashlib.sha256(self.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        if isinstance(data, str):
            return data.encode('utf8')
        return data

    def decrypt(self, enc):
        # 提取前 16 字节作为 IV
        iv = enc[:AES.block_size]
        # 创建 AES CBC 模式的解密器
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # 解密并移除填充
        decrypted = cipher.decrypt(enc[AES.block_size:])
        return unpad(decrypted, AES.block_size)

    def decrypt_string(self, enc):
        # Base64 解码加密内容
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode('utf8')
