import hashlib,os

def gen_md5(text):
    hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
    return hash_value

def get_chunks_from_file(texts_path, chunk_size=500, overlap=100):
    result = []
    for file_path in texts_path:
        print(f"reading {os.path.abspath(file_path)}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            print(file_path, len(text))
            chunks = [
                text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)
            ]
            result.extend(chunks)
    return result