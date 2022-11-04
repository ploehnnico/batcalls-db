import hashlib
import numpy as np
import io
import sqlite3

def md5hashfile(file_path : str) -> str:
	"""
	Returns md5 hash of given file	
	"""
	with open(file_path, 'rb') as stream:
		data = stream.read()
	md5hash = hashlib.md5(data).hexdigest()
	return md5hash

def iswavfile(file_path: str) -> bool:
	"""
	Returns if given file is a wav file
	"""
	with open(file_path, 'rb') as stream:
		header = stream.read(44)
	try:
		type_header = header[8:12].decode('UTF-8')
	except Exception as e:
		return False
	return type_header == 'WAVE'

def removenewline(s : str) -> str:
	s = s[:-1] if s[-1] == '\n' else s
	return s

def adapt_array(arr):
	out = io.BytesIO()
	np.save(out, arr)
	out.seek(0)
	return sqlite3.Binary(out.read())

def convert_array(text):
	out = io.BytesIO(text)
	out.seek(0)
	return np.load(out)