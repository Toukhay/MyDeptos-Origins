from flask import Blueprint, render_template, request, session, jsonify
from models import Departamento, Foto, Localidad, Favorito, Coordenada
from extensions import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    ultimos = Departamento.query.filter_by(estado='disponible')\
        .order_by(Departamento.fecha_publicacion.desc()).limit(3).all()
    localidades = [(l.id_localidad, l.nombre) for l in Localidad.query.all()]

    favoritos = []
    is_authenticated = False
    user_name = None
    if 'user_id' in session:
        is_authenticated = True
        user_name = session.get('user_name')
        favoritos = [f.id_departamento for f in
                     Favorito.query.filter_by(id_usuario=session['user_id']).all()]

    return render_template('home.html',
                           ultimos_departamentos=_format_deptos(ultimos),
                           favoritos=favoritos,
                           is_authenticated=is_authenticated,
                           user_name=user_name,
                           localidades=localidades)


@main_bp.route('/listings')
def listings():
    page = request.args.get('page', 1, type=int)
    pagination = Departamento.query.filter_by(estado='disponible')\
        .paginate(page=page, per_page=6, error_out=False)

    favoritos = []
    is_authenticated = False
    if 'user_id' in session:
        is_authenticated = True
        favoritos = [f.id_departamento for f in
                     Favorito.query.filter_by(id_usuario=session['user_id']).all()]

    return render_template('listings.html',
                           departamentos=_format_deptos(pagination.items),
                           favoritos=favoritos,
                           is_authenticated=is_authenticated,
                           page=page,
                           total_pages=pagination.pages)


@main_bp.route('/search')
def search():
    tipo_publicacion = request.args.get('tipo_publicacion')
    precio_min = request.args.get('precio_min')
    precio_max = request.args.get('precio_max')
    ambientes = request.args.get('ambientes')
    localidad = request.args.get('localidad')
    rol_inmobiliario = request.args.get('rol_inmobiliario')
    filter_lat = request.args.get('filter_lat')
    filter_lng = request.args.get('filter_lng')
    filter_radius = request.args.get('filter_radius', '2')
    page = request.args.get('page', 1, type=int)

    query = Departamento.query.filter_by(estado='disponible')

    if tipo_publicacion:
        query = query.filter(Departamento.tipo_publicacion == tipo_publicacion)
    if precio_min:
        query = query.filter(Departamento.precio >= precio_min.replace('.', '').replace(',', ''))
    if precio_max:
        query = query.filter(Departamento.precio <= precio_max.replace('.', '').replace(',', ''))
    if ambientes:
        query = query.filter(Departamento.ambientes == ambientes)
    if localidad:
        query = query.filter(Departamento.id_localidad == localidad)
    if rol_inmobiliario:
        query = query.filter(Departamento.rol_inmo_dir == rol_inmobiliario)

    if filter_lat and filter_lng:
        try:
            lat = float(filter_lat)
            lng = float(filter_lng)
            radius = float(filter_radius)
            query = query.join(Coordenada).filter(
                db.func.acos(
                    db.func.cos(db.func.radians(lat)) *
                    db.func.cos(db.func.radians(Coordenada.latitud)) *
                    db.func.cos(db.func.radians(Coordenada.longitud) - db.func.radians(lng)) +
                    db.func.sin(db.func.radians(lat)) *
                    db.func.sin(db.func.radians(Coordenada.latitud))
                ) * 6371 <= radius
            )
        except (ValueError, TypeError):
            pass

    pagination = query.paginate(page=page, per_page=6, error_out=False)

    return render_template('search_results.html',
                           resultados=_format_deptos_search(pagination.items),
                           page=page,
                           total_pages=pagination.pages)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/get_localidades')
def get_localidades():
    localidades = Localidad.query.all()
    return jsonify([(l.id_localidad, l.nombre) for l in localidades])


def _format_deptos(deptos):
    result = []
    for d in deptos:
        fotos = [f.url_foto for f in d.fotos]
        result.append((
            d.id_departamento, d.titulo, d.descripcion, d.precio,
            d.moneda, d.ambientes, d.dormitorios, d.banos,
            d.superficie, d.direccion, d.rol_inmo_dir, fotos
        ))
    return result


def _format_deptos_search(deptos):
    result = []
    for d in deptos:
        fotos = [f.url_foto for f in d.fotos]
        lat = float(d.coordenadas.latitud) if d.coordenadas else 0.0
        lng = float(d.coordenadas.longitud) if d.coordenadas else 0.0
        result.append((
            d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion,
            float(d.precio), d.moneda, d.ambientes, d.dormitorios, d.banos,
            d.superficie, d.direccion, fotos, lat, lng
        ))
    return result