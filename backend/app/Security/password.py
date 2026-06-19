import hashlib
import bcrypt

class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        """Hash password safely for bcrypt by pre-hashing to fixed length."""
        normalized = hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")
        return bcrypt.hashpw(normalized, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify password against stored bcrypt hash."""
        normalized = hashlib.sha256(plain_password.encode("utf-8")).hexdigest().encode("utf-8")
        try:
            return bcrypt.checkpw(normalized, hashed_password.encode("utf-8"))
        except ValueError:
            return False