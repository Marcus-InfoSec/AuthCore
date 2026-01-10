from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder
from config import KEYS_FILE

def load_private_key():
    with open(KEYS_FILE, "r") as f:
        private_key_b64 = f.readline().strip()
    return SigningKey(private_key_b64, encoder=Base64Encoder)

_signing_key = None

def get_signing_key():
    global _signing_key
    if _signing_key is None:
        _signing_key = load_private_key()
    return _signing_key
