import hashlib

def generate_pdf_hash(pdf_path):

    sha = hashlib.sha256()

    with open(pdf_path,"rb") as f:
        sha.update(f.read())

    return sha.hexdigest()