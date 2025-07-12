from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, SelectField, IntegerField, HiddenField
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid # Importar uuid
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user
import datetime # <--- AÑADIR ESTA IMPORTACIÓN
from dotenv import load_dotenv
from wtforms import ValidationError
import re
from datetime import datetime, timedelta
from functools import wraps

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__, static_folder="static")
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'bdmydeptos')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_secreta')

mysql = MySQL(app)
csrf = CSRFProtect(app)  # Habilitar CSRF
login_manager = LoginManager()
login_manager.init_app(app)

# -----------------------
# Clase User
# -----------------------
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

import logging
from logging.handlers import RotatingFileHandler

# Configuración básica de logs
def setup_logger():
    # Crea el directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configura el archivo de log (rotativo para no ocupar mucho espacio)
    file_handler = RotatingFileHandler(
        'logs/mydeptos.log', 
        maxBytes=10240,  # 10KB por archivo
        backupCount=10   # Mantiene 10 archivos antiguos
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MyDeptos iniciado')

# Llama a la función de configuración
setup_logger()

# -----------------------
# Función para enviar correos
# -----------------------
def send_email(to_email, subject, body):
    sender_email = os.getenv('EMAIL_USER', 'mydeptos@gmail.com')
    sender_password = os.getenv('EMAIL_PASSWORD', 'qhai btga vlfl wpyu')

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.quit()
        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# -----------------------
# Formularios
# -----------------------
class RegisterForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Repetir Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Revisa este campo, las contraseñas no coinciden')
    ])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Registrarse')

    def validate_username(self, field):
        # Solo letras y números, sin espacios ni símbolos especiales
        if not re.match(r'^[A-Za-z0-9]+$', field.data):
            raise ValidationError('El nombre de usuario solo puede contener letras y números, sin espacios ni símbolos/caracteres especiales.')
        # Verificar que el username no exista exactamente igual
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM usuario WHERE name = %s", (field.data,))
        if cur.fetchone():
            cur.close()
            raise ValidationError('El nombre de usuario ya está en uso. Elige otro.')
        cur.close()

    def validate_email(self, field):
        # No espacios y debe ser un email válido
        if ' ' in field.data:
            raise ValidationError('El correo electrónico no puede contener espacios.')
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', field.data):
            raise ValidationError('Ingresa un correo electrónico válido.')
        # Verificar que el email no exista exactamente igual
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM usuario WHERE email = %s", (field.data,))
        if cur.fetchone():
            cur.close()
            raise ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        cur.close()

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Revisa este campo, las contraseñas no coinciden')

class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class PublishDeptoForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10, max=500)])
    tipo_publicacion = SelectField('Tipo de Publicación', choices=[('venta', 'Venta'), ('alquiler', 'Alquiler')], validators=[DataRequired()])
    price = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    moneda = SelectField('Moneda', choices=[('ARS', 'Pesos'), ('USD', 'Dólares')], validators=[DataRequired()])
    ambientes = IntegerField('Ambientes', validators=[DataRequired(), NumberRange(min=1)])
    dormitorios = IntegerField('Dormitorios', validators=[DataRequired(), NumberRange(min=1)])
    banos = IntegerField('Baños', validators=[DataRequired(), NumberRange(min=1)])
    superficie = DecimalField('Superficie (m²)', validators=[DataRequired(), NumberRange(min=0)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(min=5, max=200)])
    localidad = SelectField('Localidad', choices=[], validators=[DataRequired()])
    photos = MultipleFileField('Fotos del Departamento (máximo 5)', validators=[FileAllowed(['jpg', 'png', 'webp', 'jpeg'], 'Solo se permiten imágenes')])
    rol_inmo_dir = SelectField('Rol Inmobiliario', choices=[('Dueño directo', 'Dueño Directo'), ('Inmobiliaria', 'Inmobiliaria')], validators=[DataRequired()])
    submit = SubmitField('Publicar Departamento')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Enlace de Recuperación')

class ResenaForm(FlaskForm):
    puntaje = SelectField('Puntaje', choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    comentario = TextAreaField('Comentario', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Enviar Reseña')
    
class EditResenaForm(FlaskForm):
    puntaje = SelectField('Puntaje', choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    comentario = TextAreaField('Comentario', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Actualizar Reseña')

class EditProfileForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[Length(max=30)])
    current_password = PasswordField('Contraseña Actual')
    password = PasswordField('Nueva Contraseña (opcional)')
    submit = SubmitField('Guardar Cambios')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, field):
        if field.data != self.original_username:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM usuario WHERE name = %s", (field.data,))
            user = cur.fetchone()
            cur.close()
            if user:
                raise ValidationError('El nombre de usuario ya está en uso. Elige otro.')

# -----------------------
# Rutas principales
# -----------------------

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, 
                d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir,
                GROUP_CONCAT(f.url_foto) AS url_foto
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        GROUP BY d.id_departamento
        ORDER BY d.fecha_publicacion DESC
        LIMIT 3
    ''')
    ultimos_departamentos = cursor.fetchall()

    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.close()

    # Convertir las fotos en lista (si existen)
    ultimos_departamentos = [
        (id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir,
        fotos.split(',') if fotos else [])
        for id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos in ultimos_departamentos
    ]

    # Verificar sesión para favoritos
    favoritos = []
    is_authenticated = False
    user_name = None
    if 'user_id' in session:
        is_authenticated = True
        user_id = session['user_id']
        user_name = session.get('user_name')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_departamento FROM favorito WHERE id_usuario = %s', (user_id,))
        favoritos = [row[0] for row in cursor.fetchall()]
        cursor.close()

    return render_template('home.html', ultimos_departamentos=ultimos_departamentos, favoritos=favoritos,
                        is_authenticated=is_authenticated, user_name=user_name, localidades=localidades)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# -----------------------
# Ruta de búsqueda
# -----------------------
@app.route('/search', methods=['GET'])
def search():
    # Obtener filtros desde la URL
    tipo_publicacion = request.args.get('tipo_publicacion')
    precio_min = request.args.get('precio_min')
    precio_max = request.args.get('precio_max')
    ambientes = request.args.get('ambientes')

    page = int(request.args.get('page', 1))
    per_page = 6  
    offset = (page - 1) * per_page

    # Construir la consulta dinámica
    query = '''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        WHERE 1=1
    '''
    params = []

    if tipo_publicacion:
        query += ' AND d.tipo_publicacion = %s'
        params.append(tipo_publicacion)
    if precio_min:
        query += ' AND d.precio >= %s'
        params.append(precio_min)
    if precio_max:
        query += ' AND d.precio <= %s'
        params.append(precio_max)
    if ambientes:
        query += ' AND d.ambientes = %s'
        params.append(ambientes)

    query += ' GROUP BY d.id_departamento'
    query += ' LIMIT %s OFFSET %s'
    params.extend([per_page, offset])

    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    cursor.close()

    # Obtener el total de resultados para la paginación
    count_query = 'SELECT COUNT(*) FROM departamento d WHERE 1=1'
    count_params = []
    if tipo_publicacion:
        count_query += ' AND d.tipo_publicacion = %s'
        count_params.append(tipo_publicacion)
    if precio_min:
        count_query += ' AND d.precio >= %s'
        count_params.append(precio_min)
    if precio_max:
        count_query += ' AND d.precio <= %s'
        count_params.append(precio_max)
    if ambientes:
        count_query += ' AND d.ambientes = %s'
        count_params.append(ambientes)

    cursor = mysql.connection.cursor()
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]
    cursor.close()
    total_pages = (total + per_page - 1) // per_page

    # Procesar resultados with manejo seguro de precios
    resultados_procesados = []
    for row in resultados:
        id_departamento, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, fotos = row
        
        # Manejo seguro de la conversión de precio
        try:
            if precio is not None:
                if isinstance(precio, (int, float)):
                    precio_float = float(precio)
                elif hasattr(precio, '__float__'):  # Para objetos Decimal
                    precio_float = float(precio)
                else:
                    precio_float = float(str(precio))  # Conversión desde string
            else:
                precio_float = 0.0
        except (ValueError, TypeError) as e:
            app.logger.warning(f"Error convirtiendo precio para departamento {id_departamento}: {precio}, error: {e}")
            precio_float = 0.0
        
        resultados_procesados.append((
            id_departamento, titulo, descripcion, tipo_publicacion, 
            precio_float, moneda, ambientes, dormitorios, banos, superficie, direccion, 
            fotos.split(',') if fotos else []
        ))

    # Renderizar resultados y paginación
    return render_template(
        'search_results.html',
        resultados=resultados_procesados,
        page=page,
        total_pages=total_pages
    )

# -----------------------
# Rutas de autenticación
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login_error = None
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, email, password, rol FROM usuario WHERE name = %s OR email = %s", (username, username))
        user = cur.fetchone()
        cur.close()
        if user:
            stored_hash = user[3]
            rol = user[4] if len(user) > 4 else 'user'
            if stored_hash.startswith('pbkdf2:') or stored_hash.startswith('scrypt:'):
                valid = check_password_hash(stored_hash, password)
            elif stored_hash.startswith('$2a$') or stored_hash.startswith('$2b$'):
                valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            else:
                valid = password == stored_hash
            if valid:
                user_obj = User(id=user[0], username=user[1], email=user[2])
                login_user(user_obj)
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_rol'] = rol
                # Redirección según rol
                if rol == 'admin':
                    return redirect(url_for('admin_panel'))
                else:
                    return render_template('login_redirect.html')
        login_error = "Usuario o contraseña incorrectos."
    return render_template('login.html', form=form, login_error=login_error)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    # Redirige a la pantalla de "cerrando sesión"
    return render_template('logout_redirect.html')

@app.route('/login_redirect')
def login_redirect():
    # Redirige al panel de usuario después de 5 segundos
    return render_template('login_redirect.html')

@app.route('/logout_redirect')
def logout_redirect():
    # Redirige al home después de 5 segundos
    return render_template('logout_redirect.html')

# -----------------------
# Recuperación y reseteo de contraseña
# -----------------------
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM usuario WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            token = serializer.dumps(email, salt='recover-password')
            reset_url = url_for('reset_password', token=token, _external=True)
            subject = "Recuperación de contraseña"
            body = f"Hola,\n\nPara restablecer tu contraseña, haz clic en el siguiente enlace:\n\n{reset_url}\n\nSi no solicitaste este cambio, ignora este correo."
            send_email(email, subject, body)
            flash('Hemos enviado un enlace de recuperación a tu correo.', 'info')
        else:
            flash('El correo ingresado no está registrado.', 'danger')
    return render_template('forgotpassword.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='recover-password', max_age=3600)
    except:
        flash('El enlace de recuperación ha expirado o no es válido.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE usuario SET password = %s WHERE email = %s', (hashed_password.decode('utf-8'), email))
        mysql.connection.commit()
        cursor.close()
        flash('Tu contraseña ha sido restablecida con éxito. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('resetpassword.html')

# -----------------------
# Ruta de registro + campo de confirmacion en mi archivo register.html

# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        telefono = form.telefono.data
        cur = mysql.connection.cursor()
        # Cambia el INSERT para incluir el campo rol
        cur.execute("INSERT INTO usuario (name, email, password, telefono, rol) VALUES (%s, %s, %s, %s, %s)", (username, email, password, telefono, 'user'))
        mysql.connection.commit()
        cur.close()
        # Redirige al template de éxito de registro
        return render_template('register_success.html')
    return render_template('register.html', form=form)

def get_db_connection():
    return mysql.connection

@app.route('/user_panel')
def user_panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']

    # PAGINACIÓN
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT name, email, fecha_registro, telefono FROM usuario WHERE id = %s', (user_id,))
        user_data = cur.fetchone()

        cur.execute('''
            SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion, d.precio, d.moneda, d.ambientes, 
                d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir, 
                GROUP_CONCAT(f.url_foto) AS fotos, c.latitud, c.longitud
            FROM departamento d
            LEFT JOIN foto f ON d.id_departamento = f.id_departamento
            LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
            WHERE d.id_usuario = %s
            GROUP BY d.id_departamento
            LIMIT %s OFFSET %s
        ''', (user_id, per_page, offset))
        mis_publicaciones_data = cur.fetchall()

        # Total para paginación
        cur.execute('SELECT COUNT(*) FROM departamento WHERE id_usuario = %s', (user_id,))
        total = cur.fetchone()[0]
        total_pages = (total + per_page - 1) // per_page

        # Obtener notificaciones del usuario
        cur.execute('''
            SELECT id_notificacion, tipo_notificacion, mensaje, id_departamento_ref, id_resena_ref, fecha_envio, leida
            FROM notificaciones
            WHERE id_usuario_receptor = %s
            ORDER BY fecha_envio DESC
        ''', (user_id,))
        notificaciones_data = cur.fetchall()

    except Exception as e:
        flash(f'Error al cargar datos del usuario: {e}', 'danger')
        cur.close()
        return redirect(url_for('home'))
    finally:
        if cur:
            cur.close()

    mis_publicaciones = [
        (id_dep, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos.split(',') if fotos else [], latitud, longitud)
        for id_dep, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos, latitud, longitud in mis_publicaciones_data
    ]

    notificaciones_list = []
    for row in notificaciones_data:
        notif = {
            "id": row[0], "tipo": row[1], "mensaje": row[2],
            "id_departamento_ref": row[3], "id_resena_ref": row[4],
            "fecha_envio": row[5], "leida": row[6]
        }
        notificaciones_list.append(notif)

    form = PublishDeptoForm()

    return render_template('user_panel.html', user_data=user_data, mis_publicaciones=mis_publicaciones, form=form, notificaciones=notificaciones_list, page=page, total_pages=total_pages)

@app.route('/modify_depto/<int:depto_id>', methods=['GET', 'POST'])
def modify_depto(depto_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.titulo, d.descripcion, d.tipo_publicacion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.id_localidad, d.rol_inmo_dir,
               GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        WHERE d.id_departamento = %s AND d.id_usuario = %s
        GROUP BY d.id_departamento
    ''', (depto_id, session['user_id']))
    depto_data = cursor.fetchone()

    if not depto_data:
        flash('Departamento no encontrado o no tienes permisos para editarlo.', 'danger')
        cursor.close()
        return redirect(url_for('user_panel'))

    current_photos_str = depto_data[12]
    current_photos_list = current_photos_str.split(',') if current_photos_str else []

    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()

    cursor.execute('SELECT latitud, longitud FROM coordenadas WHERE id_departamento = %s', (depto_id,))
    coords = cursor.fetchone()
    cursor.close()

    latitud = coords[0] if coords else ''
    longitud = coords[1] if coords else ''

    form = PublishDeptoForm() # Usamos el mismo formulario, pero la lógica de fotos será diferente
    form.localidad.choices = [(str(id_loc), nombre) for id_loc, nombre in localidades]
    # Hacemos que el campo de fotos no sea obligatorio para la modificación si no se quieren cambiar
    form.photos.validators = [FileAllowed(['jpg', 'png', 'webp', 'jpeg'], 'Solo se permiten imágenes')]


    if request.method == 'GET':
        form.title.data = depto_data[0]
        form.description.data = depto_data[1]
        form.tipo_publicacion.data = depto_data[2]
        form.price.data = depto_data[3]
        form.moneda.data = depto_data[4]
        form.ambientes.data = depto_data[5]
        form.dormitorios.data = depto_data[6]
        form.banos.data = depto_data[7]
        form.superficie.data = depto_data[8]
        form.direccion.data = depto_data[9]
        form.localidad.data = str(depto_data[10])
        form.rol_inmo_dir.data = depto_data[11]

    if form.validate_on_submit():
        cursor = mysql.connection.cursor()
        try:
            # Actualizar los datos del departamento
            cursor.execute('''
                UPDATE departamento SET titulo=%s, descripcion=%s, tipo_publicacion=%s, precio=%s, moneda=%s,
                    ambientes=%s, dormitorios=%s, banos=%s, superficie=%s, direccion=%s, id_localidad=%s, rol_inmo_dir=%s
                WHERE id_departamento=%s AND id_usuario=%s
            ''', (
                form.title.data, form.description.data, form.tipo_publicacion.data, form.price.data, form.moneda.data,
                form.ambientes.data, form.dormitorios.data, form.banos.data, form.superficie.data, form.direccion.data,
                form.localidad.data, form.rol_inmo_dir.data, depto_id, session['user_id']
            ))
            
            # Actualizar coordenadas
            lat = request.form.get('latitud')
            lon = request.form.get('longitud')
            cursor.execute('UPDATE coordenadas SET latitud=%s, longitud=%s WHERE id_departamento=%s', (lat, lon, depto_id))

            # Procesar imágenes si se subieron nuevas
            new_photos = request.files.getlist(form.photos.name)
            if new_photos and new_photos[0].filename: # Verificar si se subió al menos un archivo con nombre
                # Eliminar fotos antiguas de la DB y del sistema de archivos
                if current_photos_list:
                    for old_photo_filename in current_photos_list:
                        try:
                            os.remove(os.path.join(app.root_path, 'static', 'image', old_photo_filename))
                        except OSError as e:
                            app.logger.error(f"Error eliminando archivo antiguo {old_photo_filename}: {e}")
                    cursor.execute('DELETE FROM foto WHERE id_departamento = %s', (depto_id,))

                # Guardar nuevas fotos
                if len(new_photos) > 5:
                    flash('Puedes subir un máximo de 5 imágenes.', 'danger')
                    # No hacer rollback aquí, los datos del depto ya se actualizaron.
                    # Podríamos redirigir o manejarlo de otra forma.
                    # Por ahora, se guardarán las primeras 5.
                    new_photos = new_photos[:5]

                for photo_file in new_photos:
                    if photo_file.filename: # Asegurarse de que el archivo tiene nombre
                        original_filename = secure_filename(photo_file.filename)
                        # Generar un nombre de archivo único
                        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                        photo_path = os.path.join(app.root_path, 'static', 'image', unique_filename)
                        try:
                            photo_file.save(photo_path)
                            cursor.execute('INSERT INTO foto (id_departamento, url_foto) VALUES (%s, %s)', 
                                        (depto_id, unique_filename)) # Guardar el nombre único
                        except Exception as e:
                            # Si falla el guardado de una imagen, podríamos querer hacer rollback de las fotos
                            # o al menos loguear el error y continuar.
                            app.logger.error(f"Error guardando nueva imagen {original_filename}: {e}")
                            flash(f'Error al guardar la imagen {original_filename}.', 'warning')


            mysql.connection.commit()
            flash('Departamento actualizado correctamente.', 'success')
            return redirect(url_for('user_panel'))
        except Exception as e:
            mysql.connection.rollback()
            app.logger.error(f"Error actualizando departamento {depto_id}: {e}")
            flash(f'Error al actualizar el departamento: {str(e)}', 'danger')
        finally:
            cursor.close()

    return render_template('modify_depto.html', form=form, depto_id=depto_id, latitud=latitud, longitud=longitud, current_photos=current_photos_list)

@app.route('/about')
def about():
    # Aquí puedes pasar cualquier variable que necesites a la plantilla
    # Por ejemplo, si necesitas current_user para la barra de navegación
    return render_template('about.html')

@app.route('/listings')
def listings():
    page = int(request.args.get('page', 1))
    per_page = 6
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()
    # Consulta paginada
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir, GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        GROUP BY d.id_departamento
        LIMIT %s OFFSET %s
    ''', (per_page, offset))
    departamentos = cursor.fetchall()

    # Obtener el total de departamentos para paginación
    cursor.execute('SELECT COUNT(*) FROM departamento')
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    cursor.close()

    # Convertir las fotos en una lista
    departamentos = [
        (id_departamento, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos.split(',') if fotos else [])
        for id_departamento, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos in departamentos
    ]

    favoritos = []
    is_authenticated = False
    if 'user_id' in session:
        user_id = session['user_id']
        is_authenticated = True
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_departamento FROM favorito WHERE id_usuario = %s', (user_id,))
        favoritos = [row[0] for row in cursor.fetchall()]
        cursor.close()

    return render_template(
        'listings.html',
        departamentos=departamentos,
        favoritos=favoritos,
        is_authenticated=is_authenticated,
        page=page,
        total_pages=total_pages
    )

@app.route('/publish_depto', methods=['GET', 'POST'])
def publish_depto():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    form = PublishDeptoForm()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades_data = cursor.fetchall()
    cursor.close()
    form.localidad.choices = [(str(id_loc), nombre) for id_loc, nombre in localidades_data]

    if request.method == 'POST': # Mover la lógica de POST aquí para que los errores se manejen antes de renderizar
        if form.validate_on_submit():
            try:
                # Datos del formulario
                title = form.title.data
                description = form.description.data
                tipo_publicacion = form.tipo_publicacion.data
                price = form.price.data
                moneda = form.moneda.data
                ambientes = form.ambientes.data
                dormitorios = form.dormitorios.data
                banos = form.banos.data
                superficie = form.superficie.data
                direccion = form.direccion.data
                localidad = form.localidad.data
                rol_inmo_dir = form.rol_inmo_dir.data
                user_id = session['user_id']

                # Validación de coordenadas
                latitud = request.form.get('latitud')
                longitud = request.form.get('longitud')
                if not latitud or not longitud:
                    flash('Por favor, selecciona una ubicación en el mapa.', 'danger')
                    # Vuelve a renderizar el formulario con los datos y el error
                    return render_template('publish_depto.html', form=form)

                # Validación de imágenes
                photos_from_request = request.files.getlist(form.photos.name)
                # Filtrar solo las fotos que realmente tienen un archivo subido
                valid_photos = [p for p in photos_from_request if p and p.filename]

                if not (1 <= len(valid_photos) <= 5):
                    flash('Debes subir entre 1 y 5 imágenes válidas.', 'danger')
                     # Vuelve a renderizar el formulario con los datos y el error
                    return render_template('publish_depto.html', form=form)

                # Iniciar transacción
                cursor = mysql.connection.cursor()

                # Insertar departamento
                cursor.execute('''
                    INSERT INTO departamento (id_usuario, id_localidad, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fecha_publicacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ''', (user_id, localidad, title, description, tipo_publicacion, price, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir))
                departamento_id = cursor.lastrowid

                # Insertar coordenadas
                cursor.execute('INSERT INTO coordenadas (id_departamento, latitud, longitud) VALUES (%s, %s, %s)', 
                            (departamento_id, latitud, longitud))

                # Procesar cada imagen válida
                for photo in valid_photos:
                    original_filename = secure_filename(photo.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                    photo_path = os.path.join(app.root_path, 'static', 'image', unique_filename)
                    
                    try:
                        photo.save(photo_path)
                        cursor.execute('INSERT INTO foto (id_departamento, url_foto) VALUES (%s, %s)', 
                                    (departamento_id, unique_filename))
                    except Exception as e:
                        mysql.connection.rollback()
                        flash(f'Error al guardar la imagen {original_filename}: {str(e)}', 'danger')
                        return render_template('publish_depto.html', form=form) # Vuelve al form

                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('publication_success'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al publicar el departamento: {str(e)}', 'danger')
                # No redirigir, renderizar el template con el formulario para no perder datos
                return render_template('publish_depto.html', form=form)
        else:# Si form.validate_on_submit() es False
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    label = getattr(form, fieldName).label.text if hasattr(getattr(form, fieldName), 'label') else fieldName
                    flash(f"Error en el campo '{label}': {err}", 'danger')
    
    # Para GET request o si POST falla validación y necesita re-renderizar
    return render_template('publish_depto.html', form=form)

# -----------------------
# Rutas de Favoritos
# -----------------------
@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    user_id = session['user_id']
    property_id = request.form['property_id']

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO favorito (id_usuario, id_departamento, fecha_agregado) VALUES (%s, %s, NOW())',
            (user_id, property_id)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error en add_favorite: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    user_id = session['user_id']
    property_id = request.form['property_id']

    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM favorito WHERE id_usuario = %s AND id_departamento = %s', (user_id, property_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error en remove_favorite: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/viewProperty/<int:property_id>', methods=['GET', 'POST'])
def view_property(property_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, 
            d.superficie, d.direccion, d.rol_inmo_dir, GROUP_CONCAT(f.url_foto) AS fotos, 
            c.latitud, c.longitud, u.id AS user_id, u.name AS user_name, u.email AS user_email, u.telefono AS user_telefono
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
        LEFT JOIN usuario u ON d.id_usuario = u.id
        WHERE d.id_departamento = %s
        GROUP BY d.id_departamento, u.id, u.name, u.email, u.telefono
    ''', (property_id,))
    departamento_data = cursor.fetchone()

    if not departamento_data:
        cursor.close()
        flash('Propiedad no encontrada.', 'danger')
        return redirect(url_for('home'))

    departamento = {
        "id": departamento_data[0],
        "titulo": departamento_data[1],
        "descripcion": departamento_data[2],
        "precio": departamento_data[3],
        "moneda": departamento_data[4],
        "ambientes": departamento_data[5],
        "dormitorios": departamento_data[6],
        "banos": departamento_data[7],
        "superficie": departamento_data[8],
        "direccion": departamento_data[9],
        "rol_inmo_dir": departamento_data[10],
        "fotos": departamento_data[11].split(',') if departamento_data[11] else [],
        "latitud": float(departamento_data[12]) if departamento_data[12] else 0.0,
        "longitud": float(departamento_data[13]) if departamento_data[13] else 0.0,
        "propietario_id": departamento_data[14]
    }
    publicador = {
        "id": departamento_data[14],
        "nombre": departamento_data[15],
        "email": departamento_data[16],
        "telefono": departamento_data[17]
    }

    # Obtener reseñas
    cursor.execute('''
        SELECT r.id_resena, r.puntaje, r.comentario, r.fecha_calificacion, u.name AS calificador_nombre, r.id_usuario_calificador
        FROM resena r
        JOIN usuario u ON r.id_usuario_calificador = u.id
        WHERE r.id_departamento = %s
        ORDER BY r.fecha_calificacion DESC
    ''', (property_id,))
    resenas_data = cursor.fetchall()
    
    resenas = [{
        "id_resena": row[0], "puntaje": row[1], "comentario": row[2], 
        "fecha_calificacion": row[3], "calificador_nombre": row[4], 
        "id_usuario_calificador": row[5]
    } for row in resenas_data]

    current_user_id = session.get('user_id')
    user_has_reviewed = False
    user_review_id = None
    is_authenticated = 'user_id' in session
    favoritos = []

    if current_user_id:
        for resena in resenas:
            if resena['id_usuario_calificador'] == current_user_id:
                user_has_reviewed = True
                user_review_id = resena['id_resena']
                break
        # Obtener favoritos del usuario actual
        cursor.execute('SELECT id_departamento FROM favorito WHERE id_usuario = %s', (current_user_id,))
        favoritos = [row[0] for row in cursor.fetchall()]
    
    resena_form = ResenaForm()
    edit_resena_form = EditResenaForm()

    if user_has_reviewed and request.method == 'GET':
        pass

    cursor.close()
    return render_template('viewProperty.html', departamento=departamento, publicador=publicador,
                        resenas=resenas, resena_form=resena_form, edit_resena_form=edit_resena_form,
                        current_user_id=current_user_id, user_has_reviewed=user_has_reviewed,
                        user_review_id=user_review_id, is_authenticated=is_authenticated, favoritos=favoritos)

@app.route('/departamento/<int:departamento_id>/add_resena', methods=['POST'])
def add_resena(departamento_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para dejar una reseña.', 'warning')
        return redirect(url_for('login'))

    form = ResenaForm()
    if form.validate_on_submit():
        puntaje = form.puntaje.data
        comentario = form.comentario.data
        id_usuario_calificador = session['user_id']

        cursor = mysql.connection.cursor()
        
        # Verificar que el usuario no reseñe su propio departamento
        cursor.execute("SELECT id_usuario FROM departamento WHERE id_departamento = %s", (departamento_id,))
        depto_owner = cursor.fetchone()
        if depto_owner and depto_owner[0] == id_usuario_calificador:
            flash('No puedes reseñar tu propio departamento.', 'danger')
            cursor.close()
            return redirect(url_for('view_property', property_id=departamento_id))

        # Verificar si el usuario ya ha reseñado este departamento
        cursor.execute("SELECT id_resena FROM resena WHERE id_departamento = %s AND id_usuario_calificador = %s", (departamento_id, id_usuario_calificador))
        existing_resena = cursor.fetchone()
        if existing_resena:
            flash('Ya has dejado una reseña para este departamento. Puedes editarla si lo deseas.', 'info')
            cursor.close()
            return redirect(url_for('view_property', property_id=departamento_id))

        # Insertar reseña
        cursor.execute('''
            INSERT INTO resena (id_departamento, id_usuario_calificador, puntaje, comentario, fecha_calificacion)
            VALUES (%s, %s, %s, %s, NOW())
        ''', (departamento_id, id_usuario_calificador, puntaje, comentario))
        resena_id = cursor.lastrowid

        # Crear notificación para el propietario del departamento
        if depto_owner:
            propietario_id = depto_owner[0]
            # Obtener nombre del calificador y título del departamento para el mensaje
            cursor.execute("SELECT name FROM usuario WHERE id = %s", (id_usuario_calificador,))
            calificador_name_tuple = cursor.fetchone()
            cursor.execute("SELECT titulo FROM departamento WHERE id_departamento = %s", (departamento_id,))
            depto_titulo_tuple = cursor.fetchone()
            
            if calificador_name_tuple and depto_titulo_tuple:
                calificador_name = calificador_name_tuple[0]
                depto_titulo = depto_titulo_tuple[0]
                mensaje = f"El usuario '{calificador_name}' ha dejado una reseña en tu departamento '{depto_titulo}'."
                cursor.execute('''
                    INSERT INTO notificaciones (id_usuario_receptor, tipo_notificacion, mensaje, id_departamento_ref, id_resena_ref, fecha_envio, leida)
                    VALUES (%s, %s, %s, %s, %s, NOW(), 0)
                ''', (propietario_id, 'NUEVA_RESENA', mensaje, departamento_id, resena_id))
            else:
                app.logger.warning(f"No se pudo crear la notificación para la reseña {resena_id} porque faltan datos del calificador o del departamento.")

        mysql.connection.commit()
        cursor.close()
        flash('Reseña agregada exitosamente.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo '{getattr(form, field).label.text}': {error}", 'danger')
    return redirect(url_for('view_property', property_id=departamento_id))

@app.route('/resena/<int:resena_id>/edit', methods=['GET', 'POST'])
def edit_resena(resena_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para editar una reseña.', 'warning')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_departamento, id_usuario_calificador, puntaje, comentario FROM resena WHERE id_resena = %s", (resena_id,))
    resena_data = cursor.fetchone()

    if not resena_data:
        flash('Reseña no encontrada.', 'danger')
        cursor.close()
        return redirect(url_for('home'))

    id_departamento = resena_data[0]
    id_usuario_calificador = resena_data[1]

    if id_usuario_calificador != session['user_id']:
        flash('No tienes permiso para editar esta reseña.', 'danger')
        cursor.close()
        return redirect(url_for('view_property', property_id=id_departamento))

    form = EditResenaForm(request.form) # Usar EditResenaForm

    if request.method == 'POST' and form.validate():
        nuevo_puntaje = form.puntaje.data
        nuevo_comentario = form.comentario.data
        cursor.execute('''
            UPDATE resena SET puntaje = %s, comentario = %s, fecha_calificacion = NOW()
            WHERE id_resena = %s
        ''', (nuevo_puntaje, nuevo_comentario, resena_id))
        mysql.connection.commit()
        cursor.close()
        flash('Reseña actualizada exitosamente.', 'success')
        return redirect(url_for('view_property', property_id=id_departamento))
    
    if request.method == 'GET':
        form.puntaje.data = str(resena_data[2])
        form.comentario.data = resena_data[3]
    
    cursor.close()
    # Se renderiza un template específico para editar o se puede hacer en un modal en viewProperty.
    # Por simplicidad, asumimos un template 'edit_resena.html' o que se maneja con modal.
    # Si no existe edit_resena.html, esta parte necesitará ajuste.
    # Para este ejemplo, redirigimos de vuelta a la propiedad, y el usuario debe reabrir el modal/form de edición.
    # Idealmente, se pasaría el form a un template dedicado.
    return render_template('edit_resena_modal_content.html', form=form, resena_id=resena_id, property_id=id_departamento)


@app.route('/resena/<int:resena_id>/delete', methods=['POST'])
def delete_resena(resena_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para eliminar una reseña.', 'warning')
        return jsonify({'success': False, 'message': 'No autenticado'}), 401 # Devolver JSON para AJAX

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_departamento, id_usuario_calificador FROM resena WHERE id_resena = %s", (resena_id,))
    resena_data = cursor.fetchone()

    if not resena_data:
        flash('Reseña no encontrada.', 'danger')
        cursor.close()
        return jsonify({'success': False, 'message': 'Reseña no encontrada'}), 404

    id_departamento = resena_data[0]
    id_usuario_calificador = resena_data[1]

    if id_usuario_calificador != session['user_id']:
        flash('No tienes permiso para eliminar esta reseña.', 'danger')
        cursor.close()
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        # Opcional: Eliminar notificaciones asociadas a esta reseña
        cursor.execute("DELETE FROM notificaciones WHERE id_resena_ref = %s", (resena_id,))
        # Eliminar la reseña
        cursor.execute("DELETE FROM resena WHERE id_resena = %s", (resena_id,))
        mysql.connection.commit()
        flash('Reseña eliminada exitosamente.', 'success')
        cursor.close()
        return jsonify({'success': True, 'message': 'Reseña eliminada', 'redirect_url': url_for('view_property', property_id=id_departamento)})
    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"Error al eliminar reseña {resena_id}: {e}")
        flash('Error al eliminar la reseña.', 'danger')
        cursor.close()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    page = int(request.args.get('page', 1))
    per_page = 6
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, d.ambientes,
            d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir,
            GROUP_CONCAT(fo.url_foto SEPARATOR ',') AS fotos
        FROM favorito f
        JOIN departamento d ON f.id_departamento = d.id_departamento
        LEFT JOIN foto fo ON d.id_departamento = fo.id_departamento
        WHERE f.id_usuario = %s
        GROUP BY d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, 
            d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir
        LIMIT %s OFFSET %s
    ''', (user_id, per_page, offset))

    favoritos = cursor.fetchall()

    # Cambia esta consulta:
    # cursor.execute('SELECT COUNT(*) FROM favorito WHERE id_usuario = %s', (user_id,))
    # total = cursor.fetchone()[0]

    # Por esta (solo cuenta favoritos con departamento válido):
    cursor.execute('''
        SELECT COUNT(*) FROM favorito f
        JOIN departamento d ON f.id_departamento = d.id_departamento
        WHERE f.id_usuario = %s
    ''', (user_id,))
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    cursor.close()

    favoritos = [
        (
            id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir,
            fotos.split(',') if fotos else []
        )
        for id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos in favoritos
    ]

    return render_template('favorites.html', favoritos=favoritos, page=page, total_pages=total_pages)

@app.route('/get_localidades')
def get_localidades():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.close()
    return jsonify(localidades)

@app.route('/delete_publication/<int:publication_id>', methods=['POST'])
@csrf.exempt
def delete_publication(publication_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM coordenadas WHERE id_departamento = %s', (publication_id,))
        cursor.execute('DELETE FROM foto WHERE id_departamento = %s', (publication_id,))
        cursor.execute('DELETE FROM departamento WHERE id_departamento = %s AND id_usuario = %s', (publication_id, user_id))
        mysql.connection.commit()
        cursor.close()
        # Redirige directamente al template de confirmación (sin flash popup)
        return redirect(url_for('delete_confirmation'))
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar la publicación: {e}', 'danger')
        return redirect(url_for('user_panel'))

@app.route('/delete_confirmation')
def delete_confirmation():
    return render_template('delete_confirmation.html')

@app.route('/publication_success')
def publication_success():
    return render_template('publication_success.html')

print(app.url_map)

@app.context_processor
def inject_user_and_notifications():
    unread_notification_count = 0
    if 'user_id' in session:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM notificaciones WHERE id_usuario_receptor = %s AND leida = 0", (session['user_id'],))
            count_result = cursor.fetchone()
            if count_result:
                unread_notification_count = count_result[0]
            cursor.close()
        except Exception as e:
            app.logger.error(f"Error al obtener contador de notificaciones: {e}")
            unread_notification_count = 0 # Fallback
            
    return dict(current_user=current_user, unread_notification_count=unread_notification_count)

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, name, email FROM usuario WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    return None

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, email, telefono, fecha_ultima_modificacion, ediciones_ultimos_dos_dias FROM usuario WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('home'))

    last_edit = user[3]
    edit_count = user[4] if user[4] is not None else 0
    now = datetime.now()
    puede_modificar = True

    # Lógica de control de ediciones
    if last_edit:
        # Manejo robusto de formatos de fecha
        if isinstance(last_edit, datetime):
            last_edit_dt = last_edit
        else:
            last_edit_str = str(last_edit)
            try:
                last_edit_dt = datetime.strptime(last_edit_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    last_edit_dt = datetime.strptime(last_edit_str, "%Y-%m-%d")
                except ValueError:
                    # Si no se puede parsear, permitir modificar (o puedes poner puede_modificar = True)
                    last_edit_dt = now - timedelta(days=3)  # fuerza a permitir modificar
        if now - last_edit_dt > timedelta(days=2):
            edit_count = 0
        if edit_count >= 2 and now - last_edit_dt <= timedelta(days=2):
            puede_modificar = False

    form = EditProfileForm(original_username=user[0])
    # --- Inicializar los datos del formulario en GET ---
    if request.method == 'GET':
        form.username.data = user[0]
        form.email.data = user[1]
        form.telefono.data = user[2] if user[2] else ""
        # No se inicializa password ni current_password

    if form.validate_on_submit() and puede_modificar:
        new_username = form.username.data if form.username.data else user[0]
        new_email = form.email.data if form.email.data else user[1]
        new_telefono = form.telefono.data if form.telefono.data else ""
        new_password = form.password.data

        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuario SET name = %s, email = %s, password = %s, telefono = %s, fecha_ultima_modificacion = %s, ediciones_ultimos_dos_dias = %s WHERE id = %s', 
                        (new_username, new_email, hashed_password, new_telefono, now, edit_count + 1, user_id))
            mysql.connection.commit()
            cursor.close()
        else:
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuario SET name = %s, email = %s, telefono = %s, fecha_ultima_modificacion = %s, ediciones_ultimos_dos_dias = %s WHERE id = %s', 
                        (new_username, new_email, new_telefono, now, edit_count + 1, user_id))
            mysql.connection.commit()
            cursor.close()
        
        session['user_name'] = new_username
        flash('Perfil actualizado con éxito', 'success')
        return redirect(url_for('user_panel'))
    elif not puede_modificar and request.method == 'POST':
        flash('Solo puedes editar tu perfil hasta dos veces cada 2 días. Intenta nuevamente más adelante.', 'warning')
    
    return render_template('edit_profile.html', form=form, puede_modificar=puede_modificar)

@app.route('/generate_password')
def generate_password():
    secure_password = bcrypt.gensalt().decode('utf-8')
    return render_template('generate_password.html', secure_password=secure_password)

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus notificaciones.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cursor = None
    notificaciones_data = []

    try:
        cursor = mysql.connection.cursor()
        # Asegúrate de que los nombres de las columnas coincidan exactamente con tu tabla de notificaciones
        cursor.execute('''
            SELECT id_notificacion, tipo_notificacion, mensaje, id_departamento_ref, 
                id_resena_ref, fecha_envio, leida
            FROM notificaciones
            WHERE id_usuario_receptor = %s
            ORDER BY fecha_envio DESC
        ''', (user_id,))
        notificaciones_data = cursor.fetchall()
    except Exception as e:
        app.logger.error(f"Error al obtener notificaciones para el usuario {user_id}: {e}")
        flash('Ocurrió un error al cargar tus notificaciones.', 'danger')
    finally:
        if cursor:
            cursor.close()

    notificaciones_list = []
    if notificaciones_data:
        for row in notificaciones_data:
            # Asegúrate de que el orden de los índices (row[X]) coincida con el SELECT
            fecha_envio_obj = row[5]
            fecha_formateada = "Fecha no disponible"
            if isinstance(fecha_envio_obj, datetime.datetime):
                fecha_formateada = fecha_envio_obj.strftime('%Y-%m-%d %H:%M')
            
            notif = {
                "id": row[0], 
                "tipo": row[1], 
                "mensaje": row[2],
                "id_departamento_ref": row[3], 
                "id_resena_ref": row[4],
                "fecha_envio": fecha_formateada, # Usar la fecha ya formateada o el mensaje de fallback
                "leida": row[6]
            }
            notificaciones_list.append(notif)
            
    # Si el error persiste aquí, el problema podría estar en cómo Jinja2 maneja 'notifications.html'
    # o en el propio template.
    return render_template('notifications.html', notificaciones=notificaciones_list)

@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        # Asegurarse que la notificación pertenece al usuario
        cursor.execute("UPDATE notificaciones SET leida = 1 WHERE id_notificacion = %s AND id_usuario_receptor = %s AND leida = 0", (notification_id, user_id))
        mysql.connection.commit()
        
        if cursor.rowcount > 0: # Verifica si alguna fila fue actualizada
            cursor.close()
            # Podrías querer actualizar el contador de notificaciones no leídas en la sesión aquí
            # para que el badge en el header se actualice en la próxima carga completa de página.
            # Ejemplo: session['unread_notification_count'] = get_unread_notification_count_from_db(user_id)
            return jsonify({'success': True})
        else:
            # No se actualizó ninguna fila, podría ser porque ya estaba leída o no existe/no pertenece al usuario.
            # Si ya estaba leída, podemos considerarlo un éxito para la UI.
            # Verificamos si ya estaba leída.
            cursor.execute("SELECT leida FROM notificaciones WHERE id_notificacion = %s AND id_usuario_receptor = %s", (notification_id, user_id))
            notif = cursor.fetchone()
            cursor.close()
            if notif and notif[0] == 1: # Si la notificación existe y ya está leída
                return jsonify({'success': True, 'message': 'Ya estaba leída'})
            return jsonify({'success': False, 'error': 'Notificación no encontrada, no pertenece al usuario o no se pudo actualizar'}), 404
    except Exception as e:
        app.logger.error(f"Error marcando notificación como leída: {e}")
        mysql.connection.rollback() # Asegurar rollback en caso de excepción
        if 'cursor' in locals() and cursor: # type: ignore
            cursor.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401

    user_id = session['user_id']
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        # Verificar que la notificación pertenece al usuario antes de eliminar
        cursor.execute("DELETE FROM notificaciones WHERE id_notificacion = %s AND id_usuario_receptor = %s", 
                    (notification_id, user_id))
        mysql.connection.commit()

        if cursor.rowcount > 0:
            # flash('Notificación eliminada exitosamente.', 'success') # Opcional si la UI se actualiza con JS
            return jsonify({'success': True, 'message': 'Notificación eliminada'})
        else:
            return jsonify({'success': False, 'error': 'Notificación no encontrada o no tienes permiso para eliminarla'}), 404
    except Exception as e:
        mysql.connection.rollback()
        app.logger.error(f"Error eliminando notificación {notification_id} para usuario {user_id}: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar la notificación: ' + str(e)}), 500
    finally:
        if cursor:
            cursor.close()

@app.route('/notifications/mark_all_read', methods=['POST'])
def mark_all_notifications_read():
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('login')) # O devolver JSON si es para AJAX
    
    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE notificaciones SET leida = 1 WHERE id_usuario_receptor = %s AND leida = 0", (user_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Todas las notificaciones han sido marcadas como leídas.', 'success')
    except Exception as e:
        app.logger.error(f"Error marcando todas las notificaciones como leídas: {e}")
        flash('Error al marcar las notificaciones como leídas.', 'danger')
    return redirect(url_for('notifications'))

# -----------------------
# Rutas de administración
# -----------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión como administrador.', 'warning')
            return redirect(url_for('login'))
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT rol FROM usuario WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        if not user or user[0] != 'admin':
            flash('Acceso restringido solo para administradores.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_panel')
@admin_required
def admin_panel():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, telefono, rol FROM usuario")
    usuarios = cur.fetchall()
    # Listar departamentos con fotos
    cur.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir, u.name,
               GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        JOIN usuario u ON d.id_usuario = u.id
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        GROUP BY d.id_departamento
    ''')
    departamentos = cur.fetchall()
    cur.close()
    return render_template('admin_panel.html', usuarios=usuarios, departamentos=departamentos)

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    cur = mysql.connection.cursor()
    # Cambia is_admin por rol
    cur.execute("SELECT id, name, email, telefono, rol FROM usuario WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        # Cambia is_admin por rol (checkbox: si está marcado, admin; si no, user)
        rol = 'admin' if request.form.get('rol') == 'on' else 'user'
        cur.execute("UPDATE usuario SET name=%s, email=%s, telefono=%s, rol=%s WHERE id=%s",
                    (name, email, telefono, rol, user_id))
        mysql.connection.commit()
        cur.close()
        flash('Usuario actualizado.', 'success')
        return redirect(url_for('admin_panel'))
    cur.close()
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@csrf.exempt
@admin_required
def admin_delete_user(user_id):
    cur = mysql.connection.cursor()
    # Eliminar favoritos del usuario
    cur.execute("DELETE FROM favorito WHERE id_usuario = %s", (user_id,))
    # Eliminar reseñas hechas por el usuario
    cur.execute("DELETE FROM resena WHERE id_usuario_calificador = %s", (user_id,))
    # Eliminar notificaciones recibidas por el usuario
    cur.execute("DELETE FROM notificaciones WHERE id_usuario_receptor = %s", (user_id,))
    # Eliminar configuraciones de usuario si existen
    cur.execute("DELETE FROM configuracion_usuario WHERE id_usuario = %s", (user_id,))
    # Finalmente, eliminar el usuario
    cur.execute("DELETE FROM usuario WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/depto/<int:depto_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_depto(depto_id):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT id_departamento, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir FROM departamento WHERE id_departamento = %s''', (depto_id,))
    depto = cur.fetchone()
    if not depto:
        cur.close()
        flash('Departamento no encontrado.', 'danger')
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        moneda = request.form.get('moneda')
        ambientes = request.form.get('ambientes')
        dormitorios = request.form.get('dormitorios')
        banos = request.form.get('banos')
        superficie = request.form.get('superficie')
        direccion = request.form.get('direccion')
        rol_inmo_dir = request.form.get('rol_inmo_dir')
        cur.execute('''UPDATE departamento SET titulo=%s, descripcion=%s, precio=%s, moneda=%s, ambientes=%s, dormitorios=%s, banos=%s, superficie=%s, direccion=%s, rol_inmo_dir=%s WHERE id_departamento=%s''',
                    (titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, depto_id))
        mysql.connection.commit()
        cur.close()
        flash('Departamento actualizado.', 'success')
        return redirect(url_for('admin_panel'))
    cur.close()
    return render_template('admin_edit_depto.html', depto=depto)

@app.route('/admin/depto/<int:depto_id>/delete', methods=['POST', 'GET'])
@admin_required
def admin_delete_depto(depto_id):
    cur = mysql.connection.cursor()
    # Elimina primero los registros relacionados en las tablas hijas
    cur.execute("DELETE FROM clicks WHERE id_departamento = %s", (depto_id,))
    cur.execute("DELETE FROM resena WHERE id_departamento = %s", (depto_id,))
    cur.execute("DELETE FROM favorito WHERE id_departamento = %s", (depto_id,))
    cur.execute("DELETE FROM foto WHERE id_departamento = %s", (depto_id,))
    cur.execute("DELETE FROM coordenadas WHERE id_departamento = %s", (depto_id,))
    # Si tienes otras tablas con FK a departamento, agrégalas aquí

    # Ahora elimina el departamento
    cur.execute("DELETE FROM departamento WHERE id_departamento = %s", (depto_id,))
    mysql.connection.commit()
    cur.close()
    flash('Departamento eliminado correctamente.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/foto/<int:depto_id>/<foto_nombre>/delete', methods=['POST'])
@csrf.exempt
@admin_required
def admin_delete_foto(depto_id, foto_nombre):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM foto WHERE id_departamento = %s AND url_foto = %s", (depto_id, foto_nombre))
    mysql.connection.commit()
    cur.close()
    # Elimina el archivo físico si existe
    foto_path = os.path.join(app.root_path, 'static', 'image', foto_nombre)
    if os.path.exists(foto_path):
        try:
            os.remove(foto_path)
        except Exception:
            pass
    flash('Foto eliminada.', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
