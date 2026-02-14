from functools import wraps
from typing import Callable, Optional, Tuple
from flask import session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import db

def ensure_default_users() -> None:
    # Create default accounts on first run
    if db.get_user_by_username("admin") is None:
        db.create_user("admin", generate_password_hash("admin123"), role="admin", email="admin@example.com")
    if db.get_user_by_username("user") is None:
        db.create_user("user", generate_password_hash("user123"), role="user", email="user@example.com")

def login_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    u = db.get_user_by_username(username)
    if u is None:
        return False, "Unknown username."
    if not check_password_hash(u["password_hash"], password):
        return False, "Incorrect password."
    session["user_id"] = int(u["user_id"])
    session["username"] = u["username"]
    session["role"] = u["role"]
    return True, None

def logout_user() -> None:
    session.clear()

def require_login() -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("login", next=request.path))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("login", next=request.path))
            if session.get("role") != role:
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator
