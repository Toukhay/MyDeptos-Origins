from flask import Blueprint, render_template, request, session, jsonify
from extensions import mysql

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda,
               d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion, d.rol_inmo_dir,
               GROUP_CONCAT(f.url_foto) AS url_foto
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        WHERE d.estado = 'disponible'
        GROUP BY d.id_departamento
        ORDER BY d.fecha_publicacion DESC
        LIMIT 3
    ''')
    ultimos_departamentos = cursor.fetchall()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.close()

    ultimos_departamentos = [
        (id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios,
         banos, superficie, direccion, rol_inmo_dir,
         fotos.split(',') if fotos else [])
        for id_dep, titulo, descripcion, precio, moneda, ambientes, dormitorios,
            banos, superficie, direccion, rol_inmo_dir, fotos in ultimos_departamentos
    ]

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

    return render_template('home.html', ultimos_departamentos=ultimos_departamentos,
                           favoritos=favoritos, is_authenticated=is_authenticated,
                           user_name=user_name, localidades=localidades)


@main_bp.route('/listings')
def listings():
    page = int(request.args.get('page', 1))
    per_page = 6
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion,
               d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos,
               d.superficie, d.direccion, d.rol_inmo_dir,
               GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        WHERE d.estado = 'disponible'
        GROUP BY d.id_departamento
        LIMIT %s OFFSET %s
    ''', (per_page, offset))
    departamentos = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM departamento WHERE estado = "disponible"')
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    cursor.close()

    departamentos = [
        (id_dep, titulo, descripcion, tipo_pub, precio, moneda, ambientes,
         dormitorios, banos, superficie, direccion, rol,
         fotos.split(',') if fotos else [])
        for id_dep, titulo, descripcion, tipo_pub, precio, moneda, ambientes,
            dormitorios, banos, superficie, direccion, rol, fotos in departamentos
    ]

    favoritos = []
    is_authenticated = False
    if 'user_id' in session:
        is_authenticated = True
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_departamento FROM favorito WHERE id_usuario = %s',
                       (session['user_id'],))
        favoritos = [row[0] for row in cursor.fetchall()]
        cursor.close()

    return render_template('listings.html', departamentos=departamentos,
                           favoritos=favoritos, is_authenticated=is_authenticated,
                           page=page, total_pages=total_pages)


@main_bp.route('/search', methods=['GET'])
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

    page = int(request.args.get('page', 1))
    per_page = 6
    offset = (page - 1) * per_page

    query = '''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion,
               d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos,
               d.superficie, d.direccion, GROUP_CONCAT(f.url_foto) AS fotos,
               c.latitud, c.longitud
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
        WHERE d.estado = 'disponible'
    '''
    params = []

    if tipo_publicacion:
        query += ' AND d.tipo_publicacion = %s'
        params.append(tipo_publicacion)
    if precio_min:
        query += ' AND d.precio >= %s'
        params.append(precio_min.replace('.', '').replace(',', ''))
    if precio_max:
        query += ' AND d.precio <= %s'
        params.append(precio_max.replace('.', '').replace(',', ''))
    if ambientes:
        query += ' AND d.ambientes = %s'
        params.append(ambientes)
    if localidad:
        query += ' AND d.id_localidad = %s'
        params.append(localidad)
    if rol_inmobiliario:
        query += ' AND d.rol_inmo_dir = %s'
        params.append(rol_inmobiliario)
    if filter_lat and filter_lng:
        try:
            lat, lng, radius = float(filter_lat), float(filter_lng), float(filter_radius)
            query += ''' AND c.latitud IS NOT NULL AND c.longitud IS NOT NULL
                AND (6371 * acos(cos(radians(%s)) * cos(radians(c.latitud)) *
                cos(radians(c.longitud) - radians(%s)) + sin(radians(%s)) *
                sin(radians(c.latitud)))) <= %s'''
            params.extend([lat, lng, lat, radius])
        except (ValueError, TypeError):
            pass

    query += ' GROUP BY d.id_departamento LIMIT %s OFFSET %s'
    params.extend([per_page, offset])

    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    cursor.close()

    resultados_procesados = []
    for row in resultados:
        id_dep, titulo, descripcion, tipo_pub, precio, moneda, amb, dorm, ban, sup, dir_, fotos, lat, lng = row
        try:
            precio_float = float(precio) if precio is not None else 0.0
        except (ValueError, TypeError):
            precio_float = 0.0
        resultados_procesados.append((
            id_dep, titulo, descripcion, tipo_pub, precio_float, moneda,
            amb, dorm, ban, sup, dir_,
            fotos.split(',') if fotos else [], lat, lng
        ))

    cursor = mysql.connection.cursor()
    count_query = '''SELECT COUNT(*) FROM departamento d
                     LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
                     WHERE d.estado = 'disponible' '''
    count_params = []
    if tipo_publicacion:
        count_query += ' AND d.tipo_publicacion = %s'
        count_params.append(tipo_publicacion)
    if precio_min:
        count_query += ' AND d.precio >= %s'
        count_params.append(precio_min.replace('.', '').replace(',', ''))
    if precio_max:
        count_query += ' AND d.precio <= %s'
        count_params.append(precio_max.replace('.', '').replace(',', ''))
    if ambientes:
        count_query += ' AND d.ambientes = %s'
        count_params.append(ambientes)
    if localidad:
        count_query += ' AND d.id_localidad = %s'
        count_params.append(localidad)
    if rol_inmobiliario:
        count_query += ' AND d.rol_inmo_dir = %s'
        count_params.append(rol_inmobiliario)
    if filter_lat and filter_lng:
        try:
            lat, lng, radius = float(filter_lat), float(filter_lng), float(filter_radius)
            count_query += ''' AND c.latitud IS NOT NULL AND c.longitud IS NOT NULL
                AND (6371 * acos(cos(radians(%s)) * cos(radians(c.latitud)) *
                cos(radians(c.longitud) - radians(%s)) + sin(radians(%s)) *
                sin(radians(c.latitud)))) <= %s'''
            count_params.extend([lat, lng, lat, radius])
        except (ValueError, TypeError):
            pass

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]
    cursor.close()
    total_pages = (total + per_page - 1) // per_page

    return render_template('search_results.html', resultados=resultados_procesados,
                           page=page, total_pages=total_pages)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/get_localidades')
def get_localidades():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.close()
    return jsonify(localidades)