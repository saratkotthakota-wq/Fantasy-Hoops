"""Prints fresh secrets for .env:  python -m scripts.gen_keys"""
import secrets

from cryptography.fernet import Fernet

print("SESSION_SECRET=" + secrets.token_urlsafe(48))
print("ENCRYPTION_KEY=" + Fernet.generate_key().decode())
