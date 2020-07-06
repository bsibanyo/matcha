from .utils import *


def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session.keys():
            if getattr(request, 'sid', None):
                disconnect()
            return redirect(url_for("users.login"))
        return f(*args, **kwargs)
    return decorated_function


def is_extended(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session.keys() or not profile_extended(session['user']):
            return redirect(url_for("users.login"))
        return f(*args, **kwargs)
    return decorated_function


def is_anonymous(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" in session.keys():
            return redirect(url_for("home.home"))
        return f(*args, **kwargs)
    return decorated_function
