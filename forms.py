import re
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
                     DecimalField, SelectField, IntegerField)
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional, ValidationError
from extensions import mysql


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
        if not re.match(r'^[A-Za-z0-9]+$', field.data):
            raise ValidationError('Solo puede contener letras y números, sin espacios ni símbolos.')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM usuario WHERE name = %s", (field.data,))
        if cur.fetchone():
            cur.close()
            raise ValidationError('El nombre de usuario ya está en uso.')
        cur.close()

    def validate_email(self, field):
        if ' ' in field.data:
            raise ValidationError('El correo no puede contener espacios.')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM usuario WHERE email = %s", (field.data,))
        if cur.fetchone():
            cur.close()
            raise ValidationError('Ya existe una cuenta con este correo.')
        cur.close()

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Las contraseñas no coinciden.')


class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')


class PublishDeptoForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10, max=500)])
    tipo_publicacion = SelectField('Tipo de Publicación',
                                   choices=[('venta', 'Venta'), ('alquiler', 'Alquiler')],
                                   validators=[DataRequired()])
    price = StringField('Precio', validators=[DataRequired()])
    moneda = SelectField('Moneda', choices=[('ARS', 'Pesos'), ('USD', 'Dólares')],
                         validators=[DataRequired()])
    ambientes = IntegerField('Ambientes', validators=[DataRequired(), NumberRange(min=1)])
    dormitorios = IntegerField('Dormitorios', validators=[DataRequired(), NumberRange(min=1)])
    banos = IntegerField('Baños', validators=[DataRequired(), NumberRange(min=1)])
    superficie = DecimalField('Superficie (m²)', validators=[Optional(), NumberRange(min=0)], default=None)
    direccion = StringField('Dirección', validators=[DataRequired(), Length(min=5, max=200)])
    localidad = SelectField('Localidad', choices=[], validators=[DataRequired()])
    photos = MultipleFileField('Fotos (máximo 5)',
                               validators=[FileAllowed(['jpg', 'png', 'webp', 'jpeg'], 'Solo imágenes')])
    rol_inmo_dir = SelectField('Rol Inmobiliario',
                               choices=[('Dueño directo', 'Dueño Directo'), ('Inmobiliaria', 'Inmobiliaria')],
                               validators=[DataRequired()])
    submit = SubmitField('Publicar Departamento')

    def validate_price(self, field):
        price_str = str(field.data).replace('.', '').replace(',', '').strip()
        if not price_str:
            raise ValidationError('El precio es requerido.')
        if not price_str.isdigit():
            raise ValidationError('El precio debe contener solo números.')
        try:
            price_value = float(price_str)
            if price_value <= 0:
                raise ValidationError('El precio debe ser mayor a 0.')
            if price_value > 999999999:
                raise ValidationError('El precio es demasiado alto.')
        except (ValueError, TypeError):
            raise ValidationError('El precio debe ser un número válido.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Enlace de Recuperación')


class ResenaForm(FlaskForm):
    puntaje = SelectField('Puntaje', choices=[(str(i), str(i)) for i in range(1, 6)],
                          validators=[DataRequired()])
    comentario = TextAreaField('Comentario', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Enviar Reseña')


class EditResenaForm(FlaskForm):
    puntaje = SelectField('Puntaje', choices=[(str(i), str(i)) for i in range(1, 6)],
                          validators=[DataRequired()])
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
                raise ValidationError('El nombre de usuario ya está en uso.')