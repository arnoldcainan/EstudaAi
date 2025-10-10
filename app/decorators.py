# decorators.py
from functools import wraps
from flask import abort, redirect, url_for, flash,request, current_app
from flask_login import current_user
from flask import jsonify


def permission_required(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not any(getattr(current_user, perm, False) for perm in permissions):
                flash('Acesso negado! Permissão insuficiente.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso negado! Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        # acessa corretamente a API_KEY do app.config
        if api_key != current_app.config['API_KEY']:
            return jsonify({'error': 'Unauthorized access'}), 401

        return f(*args, **kwargs)

    return decorated