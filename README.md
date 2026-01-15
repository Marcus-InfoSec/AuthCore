![](pics/AuthCore.png)
# AuthCore
AuthCore is a client–server authorization and licensing core designed to protect applications from unauthorized use, response tampering, and man-in-the-middle (MITM) attacks.  The project implements a multi-layer security model that combines TLS Certificate Pinning with Ed25519 cryptographic signatures, making proxy-based attacks, fake servers.

### Distinctive Features:
- 🔐 **Ed25519** digital signature of server responses
- ⏱ Protection against **replay attacks** using timestamps
- 🔒 **TLS Certificate Pinning** (SPKI) on the client side
- 🖥 **HWID license** binding
- 🧩 **Protection against** server emulation and response spoofing
- 🐳 Complete **Docker** infrastructure
- 🤖 **Telegram bot** for license management

## 💦 Usage
1. git clone repository
```bash
git clone https://github.com/Marcus-InfoSec/AuthCore.git
```
2. rename .env.example -> .env, change fields
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=authcore
DB_USER=changeme
DB_PASSWORD=changeme

BOT_TOKEN=12345:asdbcd
ADMIN_ID=123456789

SERVER_PORT=80
KEYS_FILE=/keys/ed25519_keys.txt
```
3. run **[key_generate.py](https://github.com/Marcus-InfoSec/AuthCore/blob/main/Server/key_generate.py)**
4. open **"AuthCore/Server/server/ed25519_keys.txt".** Copy second base64 string **(public key)**
5. paste in client string.
6. run docker:
```bash
docker-compose up -d
```
7. api route: **"http://localhost/auth"**
8. get SPKI key, copy, paste in client string
```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null \
| openssl x509 -pubkey -noout \
| openssl pkey -pubin -outform DER \
| openssl dgst -sha256 -binary \
| openssl base64
```
> [!WARNING]
> AuthCore requires a valid domain name with HTTPS (SSL/TLS) enabled. Running the server on a raw IP address or without TLS is will break security.
