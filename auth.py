"""
auth.py
Handles user registration, login, and password hashing using bcrypt.
No plaintext password is ever stored in the database.
"""

import re
import bcrypt
import database


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_valid_password(password: str) -> bool:
    """Require at least 6 characters for a basic level of security."""
    return len(password) >= 6


def register_user(username: str, email: str, password: str, confirm_password: str):
    """
    Validates input and creates a new user account.
    Returns (success: bool, message: str)
    """
    username = (username or "").strip()
    email = (email or "").strip()

    if not username or not email or not password:
        return False, "All fields are required."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if not is_valid_password(password):
        return False, "Password must be at least 6 characters long."
    if password != confirm_password:
        return False, "Passwords do not match."

    existing = database.get_user_by_username(username)
    if existing:
        return False, "Username already taken."

    password_hash = hash_password(password)
    success, message = database.create_user(username, email, password_hash)
    return success, message


def login_user(username: str, password: str):
    """
    Validates login credentials.
    Returns (success: bool, message: str, user: dict or None)
    """
    username = (username or "").strip()
    user = database.get_user_by_username(username)
    if not user:
        return False, "Invalid username or password.", None
    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password.", None
    return True, "Login successful.", user