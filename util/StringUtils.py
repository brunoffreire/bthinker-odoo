from sys import exit
from binascii import unhexlify, hexlify

import base64
import hashlib
import json

class StringUtils:

    def bytes2md5(byte_data):
        hash_md5 = hashlib.md5(byte_data).hexdigest()
        return hash_md5

    def str2md5(string_data):
        byte_data = string_data.encode('utf-8')
        return StringUtils.bytes2md5(byte_data)

    def toBase64(string_data):
        byte_data = string_data.encode('utf-8')
        base64_encoded = base64.b64encode(byte_data).decode('utf-8')
        return base64_encoded

    def fromBase64(base64_data):
        byte_data = base64.b64decode(base64_data)
        string_decoded = byte_data.decode('utf-8')
        return string_decoded
    	
    def dictToJson(dict_data):
        return json.dumps(dict_data)

    @staticmethod
    def jsonToDict(json_data):
        return json.loads(json_data)