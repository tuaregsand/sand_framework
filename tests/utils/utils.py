"""Test utilities."""
import random
import string

def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def random_email() -> str:
    """Generate a random email address."""
    return f"{random_string()}@{random_string()}.com"
