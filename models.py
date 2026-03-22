from datetime import datetime
from flask_login import UserMixin
from extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(30))
    rol = db.Column(db.String(20), default='user')
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    fecha_ultima_modificacion = db.Column(db.DateTime)
    ediciones_ultimos_dos_dias = db.Column(db.Integer, default=0)

    publicaciones = db.relationship('Departamento', backref='propietario', lazy=True,
                                    foreign_keys='Departamento.id_usuario')
    favoritos = db.relationship('Favorito', backref='usuario', lazy=True)
    notificaciones = db.relationship('Notificacion', backref='receptor', lazy=True)


class Localidad(db.Model):
    __tablename__ = 'localidad'

    id_localidad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    departamentos = db.relationship('Departamento', backref='localidad', lazy=True)


class Departamento(db.Model):
    __tablename__ = 'departamento'

    id_departamento = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_localidad = db.Column(db.Integer, db.ForeignKey('localidad.id_localidad'))
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_publicacion = db.Column(db.String(20), nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    moneda = db.Column(db.String(5), default='ARS')
    ambientes = db.Column(db.Integer, nullable=False)
    dormitorios = db.Column(db.Integer, nullable=False)
    banos = db.Column(db.Integer, nullable=False)
    superficie = db.Column(db.Numeric(8, 2))
    direccion = db.Column(db.String(200), nullable=False)
    rol_inmo_dir = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), default='disponible')
    fecha_publicacion = db.Column(db.DateTime, default=datetime.now)

    fotos = db.relationship('Foto', backref='departamento', lazy=True,
                            cascade='all, delete-orphan')
    coordenadas = db.relationship('Coordenada', backref='departamento',
                                  uselist=False, cascade='all, delete-orphan')
    resenas = db.relationship('Resena', backref='departamento', lazy=True,
                              cascade='all, delete-orphan')
    favoritos = db.relationship('Favorito', backref='departamento', lazy=True,
                                cascade='all, delete-orphan')


class Foto(db.Model):
    __tablename__ = 'foto'

    id_foto = db.Column(db.Integer, primary_key=True)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamento.id_departamento'),
                                nullable=False)
    url_foto = db.Column(db.String(255), nullable=False)


class Coordenada(db.Model):
    __tablename__ = 'coordenadas'

    id = db.Column(db.Integer, primary_key=True)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamento.id_departamento'),
                                nullable=False, unique=True)
    latitud = db.Column(db.Numeric(10, 7))
    longitud = db.Column(db.Numeric(10, 7))


class Favorito(db.Model):
    __tablename__ = 'favorito'

    id_favorito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamento.id_departamento'),
                                nullable=False)
    fecha_agregado = db.Column(db.DateTime, default=datetime.now)


class Resena(db.Model):
    __tablename__ = 'resena'

    id_resena = db.Column(db.Integer, primary_key=True)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamento.id_departamento'),
                                nullable=False)
    id_usuario_calificador = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                                       nullable=False)
    puntaje = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    fecha_calificacion = db.Column(db.DateTime, default=datetime.now)

    calificador = db.relationship('Usuario', backref='resenas_hechas')


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id_notificacion = db.Column(db.Integer, primary_key=True)
    id_usuario_receptor = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo_notificacion = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    id_departamento_ref = db.Column(db.Integer, db.ForeignKey('departamento.id_departamento'))
    id_resena_ref = db.Column(db.Integer, db.ForeignKey('resena.id_resena'))
    fecha_envio = db.Column(db.DateTime, default=datetime.now)
    leida = db.Column(db.Boolean, default=False)


class ConfiguracionUsuario(db.Model):
    __tablename__ = 'configuracion_usuario'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False, unique=True)