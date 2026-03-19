from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def sign_hash(hash_value):

    with open("keys/private_key.pem","rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    signature = private_key.sign(
        bytes.fromhex(hash_value),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return signature