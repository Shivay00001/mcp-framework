import base64
import os
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import SecretStr


class SecretManager:
    """Handles encryption/decryption of connector credentials."""

    def __init__(self, master_key: str):
        self._fernet = self._derive_fernet(master_key)

    def _derive_fernet(self, master_key: str) -> Fernet:
        # In production, use a proper secret vault (HashiCorp Vault, AWS KMS)
        # Here we simulate with PBKDF2 derived key
        salt = b'mcp_salt_constant'  # Should be stored separately
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return Fernet(key)

    def encrypt(self, data: str) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self._fernet.decrypt(encrypted_data.encode()).decode()

    def secure_credentials(self, credentials: Dict[str, Any]) -> Dict[str, str]:
        """Encrypts all sensitive values in a credentials dictionary."""
        secured = {}
        for k, v in credentials.items():
            val = v.get_secret_value() if isinstance(v, SecretStr) else str(v)
            secured[k] = self.encrypt(val)
        return secured


class AuthManager:
    """Orchestrates authentication flows (OAuth2, API Keys)."""

    def __init__(self, secret_manager: SecretManager):
        self.secret_manager = secret_manager

    async def get_valid_token(self, connector_id: str, auth_config: Dict[str, Any]) -> str:
        """
        Retrieves a valid token, handling refreshes if necessary.
        This is a simplified orchestration logic.
        """
        # Logic to check token expiry and call refresh_token_url if needed
        # For now, just Decrypt and return the API Key / Token
        if "api_key" in auth_config:
            return self.secret_manager.decrypt(auth_config["api_key"])
        if "access_token" in auth_config:
            # Here we would check expiry
            return self.secret_manager.decrypt(auth_config["access_token"])
        
        raise ValueError(f"No valid auth token found for {connector_id}")
