import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

from extensions import mysql, login_manager
from forms import LoginForm, RegisterForm, ForgotPasswordForm
from utils import send_email

auth_bp = Blueprint('auth', __name__)


class User:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, name, email FROM usuario WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    return None


def _verify_password(stored_hash, password):
    """Verifica contraseña soportando bcrypt y werkzeug."""
    if stored_hash.startswith('pbkdf2:') or stored_hash.startswith('scrypt:'):
        return check_password_hash(stored_hash, password)
    elif stored_hash.startswith('$2a$') or stored_hash.startswith('$2b$'):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    return password == stored_hash


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login_error = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, name, email, password, rol FROM usuario WHERE name = %s OR email = %s",
            (username, username)
        )
        user = cur.fetchone()
        cur.close()
        if user and _verify_password(user[3], password):
            rol = user[4] if len(user) > 4 else 'user'
            user_obj = User(id=user[0], username=user[1], email=user[2])
            login_user(user_obj)
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_rol'] = rol
            if rol == 'admin':
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
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO usuario (name, email, password, telefono, rol) VALUES (%s, %s, %s, %s, %s)",
            (form.username.data, form.email.data, password, form.telefono.data, 'user')
        )
        mysql.connection.commit()
        cur.close()
        return render_template('register_success.html')
    return render_template('register.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    from flask import current_app
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM usuario WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
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
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE usuario SET password = %s WHERE email = %s',
                       (hashed.decode('utf-8'), email))
        mysql.connection.commit()
        cursor.close()
        flash('Contraseña restablecida con éxito. Podés iniciar sesión.', 'success')
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
    user_id = session['user_id']
    current_password = request.json.get('current_password', '')
    if not current_password:
        return {'success': False, 'error': 'Contraseña requerida'}
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password FROM usuario WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        if not user_data:
            return {'success': False, 'error': 'Usuario no encontrado'}
        if _verify_password(user_data[0], current_password):
            return {'success': True}
        return {'success': False, 'error': 'Contraseña incorrecta'}
    except Exception as e:
        return {'success': False, 'error': 'Error interno'}, 500