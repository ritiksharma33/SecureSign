import hashlib
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import fitz

PDF_FILE = "/Users/ritikattri/Desktop/MASTER/pdfsign/verification/signed_code.pdf"
PUBLIC_KEY = "keys/public_key.pem"

def compute_pdf_hash(pdf_path):

    sha = hashlib.sha256()

    with open(pdf_path, "rb") as f:
        sha.update(f.read())

    return sha.hexdigest()


def extract_metadata(pdf_path):

    doc = fitz.open(pdf_path)
    meta = doc.metadata
    doc.close()

    return meta


def verify_signature(pdf_hash, signature_hex, public_key_path):

    with open(public_key_path, "rb") as f:
        public_key = load_pem_public_key(f.read())

    signature = bytes.fromhex(signature_hex)

    try:
        public_key.verify(
            signature,
            pdf_hash.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return True

    except Exception:
        return False


def main():

    pdf_hash = compute_pdf_hash(PDF_FILE)

    meta = extract_metadata(PDF_FILE)

    stored_hash = meta.get("keywords")
    signature = meta.get("subject")

    print("\nComputed Hash:", pdf_hash)
    print("Stored Hash:", stored_hash)

    if pdf_hash != stored_hash:
        print("\n⚠ Document content changed!")

    valid = verify_signature(pdf_hash, signature, PUBLIC_KEY)

    if valid:
        print("\n✅ Cryptographic signature VALID")
    else:
        print("\n❌ Signature INVALID")


if __name__ == "__main__":
    main()