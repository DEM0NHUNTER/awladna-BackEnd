"""
Security_demo.py

A quick demonstration of the core security utilities in your FastAPI backend.
Shows:
 1) Password hashing & verification
 2) JWT access token creation & decoding
 3) Refresh token creation & validation
 4) Password-reset token flow
 5) Email-verification token flow
 6) Symmetric data encryption & decryption

Run this script to see example inputs and outputs for each function.
"""

# Import all necessary security-related utility functions for hashing, tokens, and verification
from BackEnd.Utils.security import (
    get_password_hash, verify_password,
    create_access_token, decode_token,
    create_refresh_token, validate_refresh_token,
    generate_password_reset_token, verify_password_reset_token,
    generate_verification_token, verify_email_token,
)

# Import encryption/decryption utilities for symmetric data encryption
from BackEnd.Utils.encryption import encrypt_data, decrypt_data

# Import to load environment variables from a .env file, like secret keys, salts, etc.
from dotenv import load_dotenv

# Load environment variables into the OS environment (required for secret keys etc.)
load_dotenv()

# ------------------------------
# 1) Password hashing & verification demonstration
# ------------------------------
password = "SuperSecret123!"  # Plaintext password for demo

# Hash the plaintext password securely
hashed = get_password_hash(password)

print("1) Password hashing")
print("   Hashed password:", hashed)
# Verify the correct password against the hash (should be True)
print("   Verify correct:", verify_password(password, hashed))
# Verify an incorrect password (should be False)
print("   Verify wrong:  ", verify_password("WrongPassword", hashed))
print()

# ------------------------------
# 2) JWT access token creation & decoding demonstration
# ------------------------------
# Create an access token with payload containing a subject (email)
token = create_access_token({"sub": "alice@example.com"})

print("2) JWT access-token")
print("   Token:", token)
# Decode the JWT token back to its payload dictionary
print("   Decoded payload:", decode_token(token))
print()

# ------------------------------
# 3) Refresh token creation & validation demonstration
# ------------------------------
# Create a refresh token for the given user email
refresh = create_refresh_token("alice@example.com")

print("3) Refresh token")
print("   Token:", refresh)
# Validate the refresh token and extract the associated email
print("   Validated email:", validate_refresh_token(refresh))
print()

# ------------------------------
# 4) Password-reset token generation & verification demonstration
# ------------------------------
# Generate a token for password reset purposes
pwd_reset = generate_password_reset_token("alice@example.com")

print("4) Password-reset token")
print("   Token:", pwd_reset)
# Verify the password reset token and retrieve the email if valid
print("   Verified email:", verify_password_reset_token(pwd_reset))
print()

# ------------------------------
# 5) Email-verification token generation & verification demonstration
# ------------------------------
# Generate an email verification token for confirming user email
email_tok = generate_verification_token("bob@example.com")

print("5) Email-verification token")
print("   Token:", email_tok)
# Verify the email verification token and extract the email if valid
print("   Verified email:", verify_email_token(email_tok))
print()

# ------------------------------
# 6) Symmetric data encryption & decryption demonstration
# ------------------------------
plaintext = "Sensitive payload"  # Example sensitive data

# Encrypt the plaintext data
ciphertext = encrypt_data(plaintext)

print("6) Data encryption")
print("   Encrypted:", ciphertext)
# Decrypt the encrypted data back to original plaintext
print("   Decrypted:", decrypt_data(ciphertext))
