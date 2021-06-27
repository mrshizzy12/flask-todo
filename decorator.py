from flask import session, redirect, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged-in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper
    