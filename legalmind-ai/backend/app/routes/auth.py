"""Authentication routes for LegalMind AI."""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.services.auth_service import register_user, authenticate_user, verify_enrollment_preview
from app.utils.auth_utils import login_required, get_current_user, login_user, logout_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new advocate after Bar Council verification."""
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('cases.dashboard'))

    if request.method == 'GET':
        return render_template('auth/register.html')

    data = request.get_json() or request.form
    enrollment_number = data.get('enrollment_number', '').strip().upper()
    name = data.get('name', '').strip()
    password = data.get('password', '')
    state = data.get('state', '').strip()

    if not all([enrollment_number, name, password, state]):
        return jsonify({'error': 'name, enrollment_number, state and password are required'}), 400

    payload, status = register_user(enrollment_number, name, state, password)
    if request.is_json:
        return jsonify(payload), status

    if status >= 400:
        return render_template('auth/register.html', error=payload.get('error')), status

    return redirect(url_for('auth.login'))


@auth_bp.route('/register/verify', methods=['POST'])
def verify_enrollment():
    """Preview registry verification for the registration prototype."""
    data = request.get_json() or request.form
    enrollment_number = data.get('enrollment_number', '').strip().upper()
    state = data.get('state', '').strip()

    if not enrollment_number or not state:
        return jsonify({
            'verified': False,
            'message': 'Please enter enrollment number and state first.',
        }), 400

    payload, status = verify_enrollment_preview(enrollment_number, state)
    return jsonify(payload), status


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate an advocate with enrollment number and password."""
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('cases.dashboard'))

    if request.method == 'GET':
        return render_template('auth/login.html')

    data = request.get_json() or request.form
    enrollment_number = data.get('enrollment_number', '').strip().upper()
    password = data.get('password', '')

    if not all([enrollment_number, password]):
        payload = {'error': 'enrollment_number and password are required'}
        if request.is_json:
            return jsonify(payload), 400
        return render_template('auth/login.html', error=payload['error']), 400

    user = authenticate_user(enrollment_number, password)
    if not user:
        payload = {'error': 'Invalid enrollment number or password'}
        if request.is_json:
            return jsonify(payload), 401
        return render_template('auth/login.html', error=payload['error']), 401

    login_user(user)
    if request.is_json:
        return jsonify({'message': 'Login successful', 'redirect': url_for('cases.dashboard')}), 200
    return redirect(url_for('cases.dashboard'))


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Log out the current advocate."""
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Return the authenticated advocate profile."""
    current_user = get_current_user()
    if request.accept_mimetypes.best == 'text/html':
        return render_template('auth/profile.html', current_user=current_user)
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'enrollment_number': current_user.enrollment_number,
        'state': current_user.state,
        'is_verified': current_user.is_verified,
        'is_admin': current_user.is_admin,
    }), 200
