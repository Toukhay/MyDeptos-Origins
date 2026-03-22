import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

from extensions import db, login_manager
from models import Usuario
from forms import LoginForm, RegisterForm, ForgotPasswordForm
from utils import send_email

auth_bp = Blueprint('auth', __name__)


def _verify_password(stored_hash, password):
    if stored_hash.startswith('pbkdf2:') or stored_hash.startswith('scrypt:'):
        return check_password_hash(stored_hash, password)
    elif stored_hash.startswith('$2a$') or stored_hash.startswith('$2b$'):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    return password == stored_hash


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login_error = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Usuario.query.filter(
            (Usuario.name == username) | (Usuario.email == username)
        ).first()
        if user and _verify_password(user.password, password):
            login_user(user)
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_rol'] = user.rol
            if user.rol == 'admin':
                return redirect(url_for('admin.admin_panel'))
            return render_template('login_redirect.html')
        login_error = "Usuario o contraseña incorrectos."
    return render_template('login.html', form=form, login_error=login_error)


@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return render_template('logout_redirect.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = Usuario(
            name=form.username.data,
            email=form.email.data,
            password=hashed,
            telefono=form.telefono.data,
            rol='user'
        )
        db.session.add(user)
        db.session.commit()
        return render_template('register_success.html')
    return render_template('register.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    from flask import current_app
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Usuario.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='recover-password')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(email, "Recuperación de contraseña",
                       f"Para restablecer tu contraseña, hacé clic aquí:\n\n{reset_url}")
            flash('Enviamos un enlace de recuperación a tu correo.', 'info')
        else:
            flash('El correo ingresado no está registrado.', 'danger')
    return render_template('forgotpassword.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='recover-password', max_age=3600)
    except Exception:
        flash('El enlace ha expirado o no es válido.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user = Usuario.query.filter_by(email=email).first()
        if user:
            user.password = bcrypt.hashpw(
                new_password.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            db.session.commit()
            flash('Contraseña restablecida. Podés iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('resetpassword.html')


@auth_bp.route('/login_redirect')
def login_redirect():
    return render_template('login_redirect.html')


@auth_bp.route('/logout_redirect')
def logout_redirect():
    return render_template('logout_redirect.html')


@auth_bp.route('/verify_current_password', methods=['POST'])
def verify_current_password():
    if 'user_id' not in session:
        return {'success': False, 'error': 'No autenticado'}, 401
    user = Usuario.query.get(session['user_id'])
    if not user:
        return {'success': False, 'error': 'Usuario no encontrado'}
    current_password = request.json.get('current_password', '')
    if _verify_password(user.password, current_password):
        return {'success': True}
    return {'success': False, 'error': 'Contraseña incorrecta'}