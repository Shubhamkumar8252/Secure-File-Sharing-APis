from cryptography.fernet import Fernet

# NOTE: Save this key securely in production!
fernet_key = Fernet.generate_key()
cipher = Fernet(fernet_key)

def encrypt(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()
