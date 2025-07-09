# BackEnd/demo/Authentication_Flow_Demo.py

# Import authentication-related utility functions and user roles
from BackEnd.Utils.auth_utils import (
    register_user,
    login_user,
    access_protected_resource,
    require_role,
    verify_email_token_and_mark_verified,
)
from BackEnd.Utils.token_store import token_store
from BackEnd.Models.user import UserRole


# Mock implementation of an in-memory Redis-like store for tokens
class InMemoryMock:
    def __init__(self):
        self.store = {}

    # Simulate Redis SETEX command (set key with TTL)
    def setex(self, key, ttl, val):
        self.store[key] = (val, ttl)

    # Simulate Redis GET command
    def get(self, key):
        return self.store.get(key, (None, None))[0]

    # Simulate Redis DEL command
    def delete(self, key):
        self.store.pop(key, None)


# Replace the real Redis client in token_store with our in-memory mock for demo/testing
token_store.redis = InMemoryMock()


def demo_authentication_flow():
    # Step 0: User inputs email and password for registration/login
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()

    # Step 1: Register the user with the provided email and password
    print("\n--- STEP 1: Registration ---")
    user = register_user(email, password)
    if not user:
        print("[ERROR] Registration failed (email may already be in use).")
        return
    print(f"[INFO] Registered user: {user.email!r}, Role: {user.role}")

    # Step 2: Simulate sending a verification email with token
    print("\n--- STEP 2: Email Verification ---")
    token = user.verification_token
    print(f"[DEBUG] Verification token (simulate sending via email): {token}")

    # Verify the token and mark the user's email as verified
    verified_user = verify_email_token_and_mark_verified(token)
    if not verified_user or not verified_user.is_verified:
        print("[ERROR] Email verification failed or token expired.")
        return
    print(f"[INFO] Email verified for: {verified_user.email}")

    # Step 3: Login the user using their credentials
    print("\n--- STEP 3: Login ---")
    access_token, refresh_token = login_user(email, password)
    if not access_token:
        print("[ERROR] Login failed.")
        return
    print(f"[INFO] Obtained access token: {access_token[:30]}...")

    # Step 4: Access a protected resource using the access token
    print("\n--- STEP 4: Access Protected Resource ---")
    access_protected_resource(access_token)

    # Step 5: Check if the verified user has the required role (e.g., PARENT)
    print("\n--- STEP 5: Role Check ---")
    try:
        require_role(UserRole.PARENT)(verified_user)
        print("[INFO] Role check passed.")
    except Exception as e:
        print("[ERROR]", e)

    # Note: The demo skips async token_store calls for simplicity.
    print("[INFO] Demo flow complete.")


# Run the demo if this script is executed directly
if __name__ == "__main__":
    demo_authentication_flow()
