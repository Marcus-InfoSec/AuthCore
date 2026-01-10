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
