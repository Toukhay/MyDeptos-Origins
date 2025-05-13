from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, SelectField, IntegerField
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, NumberRange
import bcrypt
from flask_mysqldb import MySQL
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user

app = Flask(__name__, static_folder="static")
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bdmydeptos'
app.config['SECRET_KEY'] = 'tu_clave_secreta'

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
    sender_email = "mydeptos@gmail.com"
    sender_password = "qhai btga vlfl wpyu"  # Verifica credenciales

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
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

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
    tipo_publicacion = request.args.get('tipo_publicacion')
    rol_inmobiliario = request.args.get('rol_inmobiliario')
    precio_min = request.args.get('precio_min')
    precio_max = request.args.get('precio_max')
    localidad = request.args.get('localidad')
    ambientes = request.args.get('ambientes')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()

    query = '''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, 
            d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir,
            GROUP_CONCAT(f.url_foto) AS url_foto
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        WHERE 1=1
    '''
    params = []

    if tipo_publicacion:
        query += " AND d.tipo_publicacion = %s"
        params.append(tipo_publicacion)
    if rol_inmobiliario:
        query += " AND d.rol_inmo_dir = %s"
        params.append(rol_inmobiliario)
    if precio_min:
        query += " AND d.precio >= %s"
        params.append(precio_min)
    if precio_max:
        query += " AND d.precio <= %s"
        params.append(precio_max)
    if localidad:
        query += " AND d.id_localidad = %s"
        params.append(localidad)
    if ambientes:
        query += " AND d.ambientes = %s"
        params.append(ambientes)

    query += " GROUP BY d.id_departamento"

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    cursor.close()

    # Convertir las fotos en lista (si existen)
    resultados = [
        (id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir,
        fotos.split(',') if fotos else [])
        for id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos in resultados
    ]

    return render_template('search_results.html', resultados=resultados, localidades=localidades)

# -----------------------
# Rutas de autenticación
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data.encode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, name, email, password FROM usuario WHERE name = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
            user_obj = User(id=user[0], username=user[1], email=user[2])
            login_user(user_obj)  # Marca al usuario como autenticado
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()  # Cierra la sesión del usuario
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('home'))  # Redirige al inicio

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
# Ruta de registro
# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.username.data
            email = form.email.data
            password = form.password.data
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            try:
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO usuario(name, email, password) VALUES(%s, %s, %s)', 
                            (name, email, hashed_password.decode('utf-8')))
                mysql.connection.commit()
                cursor.close()
                flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error al registrar usuario: {e}', 'danger')
        else:
            flash('Error en el formulario de registro', 'danger')
    return render_template('register.html', form=form)

# -----------------------
# Ruta para probar conexión a la BD
# -----------------------
@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return "Conexión a la base de datos exitosa"
    except Exception as e:
        return f"Error en la base de datos: {str(e)}"

def get_db_connection():
    return mysql.connection

@app.route('/user_panel')
def user_panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT name, email, fecha_registro FROM usuario WHERE id = %s', (user_id,))
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
        ''', (user_id,))
        mis_publicaciones = cur.fetchall()
    except Exception as e:
        flash(f'Error al cargar datos del usuario: {e}', 'danger')
        return redirect(url_for('home'))
    finally:
        cur.close()

    # Convertir las fotos en lista (si existen)
    mis_publicaciones = [
        (id_dep, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos.split(',') if fotos else [], latitud, longitud)
        for id_dep, titulo, descripcion, tipo_publicacion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos, latitud, longitud in mis_publicaciones
    ]

    form = PublishDeptoForm()  # Crear una instancia del formulario para obtener el token CSRF

    return render_template('user_panel.html', user_data=user_data, mis_publicaciones=mis_publicaciones, form=form)

class EditProfileForm(FlaskForm):
    username = StringField('Nuevo Usuario', validators=[Length(min=4, max=25)])
    email = StringField('Nuevo Email', validators=[Email()])
    password = PasswordField('Nueva Contraseña')
    submit = SubmitField('Actualizar Perfil')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT name, email FROM usuario WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    form = EditProfileForm()
    if request.method == 'GET':
        form.username.data = user[0]
        form.email.data = user[1]

    if form.validate_on_submit():
        new_username = form.username.data if form.username.data else user[0]
        new_email = form.email.data if form.email.data else user[1]
        new_password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM usuario WHERE name = %s AND id != %s', (new_username, user_id))
        existing_user = cursor.fetchone()
        if existing_user:
            flash(f'El nombre de usuario "{new_username}" ya está en uso. Por favor, elige otro.', 'danger')
            return render_template('edit_profile.html', form=form)
        
        cursor.execute('SELECT id FROM usuario WHERE email = %s AND id != %s', (new_email, user_id))
        existing_email = cursor.fetchone()
        if existing_email:
            flash(f'El correo electrónico "{new_email}" ya está en uso. Por favor, elige otro.', 'danger')
            return render_template('edit_profile.html', form=form)
        
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('UPDATE usuario SET name = %s, email = %s, password = %s WHERE id = %s', 
                        (new_username, new_email, hashed_password, user_id))
        else:
            cursor.execute('UPDATE usuario SET name = %s, email = %s WHERE id = %s', 
                        (new_username, new_email, user_id))
        
        mysql.connection.commit()
        cursor.close()
        
        session['user_name'] = new_username
        flash('Perfil actualizado con éxito', 'success')  # Mensaje flash
        return redirect(url_for('home'))  # Redirige al home.html
    
    return render_template('edit_profile.html', form=form)

@app.route('/generate_password')
def generate_password():
    secure_password = bcrypt.gensalt().decode('utf-8')
    return render_template('generate_password.html', secure_password=secure_password)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/listings')
def listings():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir, GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        GROUP BY d.id_departamento
    ''')
    departamentos = cursor.fetchall()
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

    return render_template('listings.html', departamentos=departamentos, favoritos=favoritos, is_authenticated=is_authenticated)

@app.route('/publish_depto', methods=['GET', 'POST'])
def publish_depto():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    form = PublishDeptoForm()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.close()
    form.localidad.choices = [(str(id), nombre) for id, nombre in localidades]

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
                return redirect(url_for('publish_depto'))

            # Validación de imágenes
            photos = request.files.getlist(form.photos.name)
            if len(photos) < 1 or len(photos) > 5:
                flash('Debes subir entre 1 y 5 imágenes.', 'error')
                return redirect(url_for('publish_depto'))

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

            # Procesar cada imagen
            for photo in photos:
                if photo.filename == '':  # Saltar si no hay archivo
                    continue
                    
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.root_path, 'static', 'image', filename)
                
                try:
                    photo.save(photo_path)
                    cursor.execute('INSERT INTO foto (id_departamento, url_foto) VALUES (%s, %s)', 
                                (departamento_id, filename))
                except Exception as e:
                    mysql.connection.rollback()
                    flash(f'Error al guardar las imágenes: {str(e)}', 'danger')
                    return redirect(url_for('publish_depto'))

            mysql.connection.commit()
            cursor.close()

            flash('Departamento publicado con éxito', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al publicar el departamento: {str(e)}', 'danger')
            return redirect(url_for('publish_depto'))

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

@app.route('/viewProperty/<int:property_id>')
def view_property(property_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos, 
               d.superficie, d.direccion, d.rol_inmo_dir, GROUP_CONCAT(f.url_foto) AS fotos, 
               c.latitud, c.longitud, u.name, u.email
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
        LEFT JOIN usuario u ON d.id_usuario = u.id
        WHERE d.id_departamento = %s
    ''', (property_id,))
    departamento_data = cursor.fetchone()
    cursor.close()

    if departamento_data:
        print(f"Latitud: {departamento_data[12]}, Longitud: {departamento_data[13]}")
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
            "longitud": float(departamento_data[13]) if departamento_data[13] else 0.0
        }
        publicador = {
            "nombre": departamento_data[14],  # name del usuario
            "email": departamento_data[15]    # email del usuario
        }
        user = session.get('user_id')
        return render_template('viewProperty.html', departamento=departamento, user=user, publicador=publicador)
    else:
        return "Propiedad no encontrada", 404

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
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
    ''', (user_id,))

    favoritos = cursor.fetchall()
    cursor.close()

    favoritos = [
        (
            id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir,
            fotos.split(',') if fotos else []  # Si hay imágenes, las convierte en lista
        )
        for id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios, banos, superficie, direccion, rol_inmo_dir, fotos in favoritos
    ]

    return render_template('favorites.html', favoritos=favoritos)

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

        # Eliminar coordenadas relacionadas
        cursor.execute('DELETE FROM coordenadas WHERE id_departamento = %s', (publication_id,))
        # Eliminar fotos relacionadas
        cursor.execute('DELETE FROM foto WHERE id_departamento = %s', (publication_id,))
        # Eliminar el departamento
        cursor.execute('DELETE FROM departamento WHERE id_departamento = %s AND id_usuario = %s', (publication_id, user_id))
        
        mysql.connection.commit()
        cursor.close()

        flash('Publicación eliminada con éxito', 'success')
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
def inject_user():
    return dict(current_user=current_user)

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, name, email FROM usuario WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    return None

if __name__ == '__main__':
    app.run(debug=True)
