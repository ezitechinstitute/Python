# utils/auth.py

ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "ezitech123"  # 🔒 Change in production
}

def verify_login(username: str, password: str) -> bool:
    return (
        username == ADMIN_CREDENTIALS["username"] and
        password == ADMIN_CREDENTIALS["password"]
    )
