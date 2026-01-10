import os
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder

KEYS_FILE = "server/ed25519_keys.txt"


def generate_and_save_keys():
    if os.path.exists(KEYS_FILE):
        raise RuntimeError("ed25519_keys.txt already exists. Refusing to overwrite.")

    signing_key = SigningKey.generate()

    private_key_b64 = signing_key.encode(
        encoder=Base64Encoder
    ).decode()

    public_key_b64 = signing_key.verify_key.encode(
        encoder=Base64Encoder
    ).decode()

    with open(KEYS_FILE, "w") as f:
        f.write(private_key_b64 + "\n")
        f.write(public_key_b64 + "\n")

    print("[+] Keys successfully generated")
    print("[+] Saved to:", KEYS_FILE)


if __name__ == "__main__":
    generate_and_save_keys()
