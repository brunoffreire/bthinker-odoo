from sys import exit
from binascii import unhexlify, hexlify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

class ZKAES:

	def __init__(self, block_size=16):
		self.key = bytes("zkteco@28111981!", "UTF-8")
		self.iv = bytes("fpmanager@zkteco", "UTF-8")
		self.block_size = block_size

	
	def encrypt(self, str):
		raw = str.encode("utf-8")
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		return cipher.encrypt(pad(raw, self.block_size))

	def decrypt(self, enc):		
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		return unpad(cipher.decrypt(enc), self.block_size)


	# Código Antigo - Desativado
	# def encrypt(self, message):
	# 	cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
	# 	pad_text = self.encode(message)
	# 	result = cipher.encrypt(pad_text)
	# 	return result
	
	# def decrypt(self, message):
	# 	cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
	# 	out = cipher.decrypt(message)
	# 	return self.decode(out)

	# def __pad(self, text):
	# 	text_length = len(text)
	# 	amount_to_pad = self.block_size - (text_length % self.block_size)
	# 	if amount_to_pad == 0:
	# 		amount_to_pad = self.block_size
	# 	pad = unhexlify('%02x' % amount_to_pad)
	# 	return text + (pad * amount_to_pad).decode("utf-8")
			
	# def __unpad(self, text):
	# 	pad = ord(text[-1])
	# 	return text[:-pad]
