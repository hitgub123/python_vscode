import hashlib

def gen_md5(text):
    hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hash_value