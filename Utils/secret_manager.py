# BackEnd/Utils/secret_manager.py

import os
from cryptography.fernet import Fernet


class SecretManager:
    @staticmethod
    def rotate_keys():
        """Run monthly via cron job"""
        new_key = Fernet.generate_key()
        old_key = os.getenv("APP_ENCRYPTION_KEY")

        # Add re-encryption logic for existing data
        # Store new key in environment
        os.environ["APP_ENCRYPTION_KEY"] = new_key.decode()

        return new_key, old_key
