# BackEnd/Utils/encryption.py

import os
from cryptography.fernet import Fernet, InvalidToken

_test_key = None  # Holds a test key for use in testing mode


def _get_fernet() -> Fernet:
    """
    Returns a Fernet instance for encryption/decryption.
    If the environment variable TESTING is set to '1' or 'true',
    a generated test key is reused to ensure consistent encryption
    during tests.

    Otherwise, retrieves the encryption key from APP_ENCRYPTION_KEY
    environment variable. Raises an error if key is missing.
    """
    if os.getenv("TESTING", "").lower() in ("1", "true"):
        global _test_key
        if _test_key is None:
            _test_key = Fernet.generate_key()  # Generate a random test key once
        return Fernet(_test_key)

    key = os.getenv("APP_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("APP_ENCRYPTION_KEY environment variable is not set!")
    return Fernet(key)


def encrypt_data(data: str) -> str:
    """
    Encrypts a plaintext string using Fernet symmetric encryption,
    returns the encrypted data as a UTF-8 string.
    """
    return _get_fernet().encrypt(data.encode()).decode()


def decrypt_data(token: str) -> str:
    """
    Decrypts an encrypted token string back to plaintext.
    Raises InvalidToken if the token is invalid or corrupted.
    """
    return _get_fernet().decrypt(token.encode()).decode()


def safe_decrypt(token: str, default: str = "") -> str:
    """
    Attempts to decrypt a token safely.
    Returns the decrypted string if successful,
    otherwise returns the provided default value (empty string by default).
    """
    try:
        return decrypt_data(token)
    except InvalidToken:
        return default
