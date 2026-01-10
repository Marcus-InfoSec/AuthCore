import os

#db
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "authcore")
DB_USER = os.getenv("DB_USER", "changeme")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

#server
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

#keys
KEYS_FILE = os.getenv("KEYS_FILE", "/keys/ed25519_keys.txt")

#bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
