from flask import Blueprint, send_from_directory, session, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'rol' not in session or session['rol'] != role:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main_bp.route('/')
def home():
    # Página pública (login o landing)
    return send_from_directory('static', 'index.html')

@main_bp.route('/sign-up.html')
def sign_up_page():
    # Página pública de registro
    return send_from_directory('static', 'sign-up.html')

@main_bp.route('/estudiante/dashboard')
@login_required
@role_required('estudiante')
def estudiante_dashboard():
    return send_from_directory('static', 'e_dashboard.html')

@main_bp.route('/tutor_academico/dashboard')
@login_required
@role_required('tutor_academico')
def tutor_academico_dashboard():
    return send_from_directory('static', 'tutor_academico_dashboard.html')

@main_bp.route('/tutor_empresarial/dashboard')
@login_required
@role_required('tutor_empresarial')
def tutor_dashboard():
    return send_from_directory('static', 'tutor_dashboard.html')
