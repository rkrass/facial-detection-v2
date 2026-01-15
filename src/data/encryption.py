"""Data encryption for session logs."""

import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


class DataEncryption:
    """Handles encryption and decryption of session data."""

    def __init__(self, password: str, iterations: int = 100000):
        """
        Initialize encryption with a password.

        Args:
            password: Password for encryption/decryption
            iterations: Number of PBKDF2 iterations
        """
        self.password = password.encode()
        self.iterations = iterations
        self.salt = None
        self.key = None

    def generate_key(self, salt: bytes = None) -> bytes:
        """
        Generate encryption key from password.

        Args:
            salt: Optional salt (generates new one if not provided)

        Returns:
            Encryption key
        """
        if salt is None:
            salt = os.urandom(16)

        self.salt = salt

        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iterations,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self.key = key
        return key

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data.

        Args:
            data: Raw data to encrypt

        Returns:
            Encrypted data (includes salt)
        """
        if self.key is None:
            self.generate_key()

        # Create Fernet cipher
        f = Fernet(self.key)

        # Encrypt data
        encrypted = f.encrypt(data)

        # Prepend salt to encrypted data
        return self.salt + encrypted

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data.

        Args:
            encrypted_data: Encrypted data (includes salt)

        Returns:
            Decrypted data
        """
        # Extract salt from beginning
        salt = encrypted_data[:16]
        encrypted = encrypted_data[16:]

        # Generate key with extracted salt
        self.generate_key(salt)

        # Create Fernet cipher
        f = Fernet(self.key)

        # Decrypt
        return f.decrypt(encrypted)

    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Encrypt a file.

        Args:
            input_path: Path to input file
            output_path: Path to encrypted output file
        """
        with open(input_path, 'rb') as f:
            data = f.read()

        encrypted = self.encrypt(data)

        with open(output_path, 'wb') as f:
            f.write(encrypted)

    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Decrypt a file.

        Args:
            input_path: Path to encrypted file
            output_path: Path to decrypted output file
        """
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted = self.decrypt(encrypted_data)

        with open(output_path, 'wb') as f:
            f.write(decrypted)
