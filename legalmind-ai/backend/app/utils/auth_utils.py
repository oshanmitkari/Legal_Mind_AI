"""Authentication utilities for session-based access control."""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from app.models import User


def get_current_user():
    """Return the logged-in User based on Flask session."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def login_user(user):
    """Store the authenticated user in the Flask session."""
    session.clear()
    session['user_id'] = user.id
    session.permanent = True


def logout_user():
    """Clear the Flask session to log out the user."""
    session.clear()


def login_required(view):
    """Require a logged-in user for the decorated view."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not get_current_user():
            if request.method in ('GET', 'HEAD'):
                return redirect(url_for('auth.login'))
            return jsonify({'error': 'Authentication required'}), 401
        return view(*args, **kwargs)
    return wrapped_view
