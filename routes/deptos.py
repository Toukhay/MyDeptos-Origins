import os
import uuid
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify)
from werkzeug.utils import secure_filename

from extensions import mysql
from forms import PublishDeptoForm, ResenaForm, EditResenaForm

deptos_bp = Blueprint('deptos', __name__)


@deptos_bp.route('/viewProperty/<int:property_id>', methods=['GET', 'POST'])
def view_property(property_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion,
               d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos,
               d.superficie, d.direccion, d.rol_inmo_dir,
               GROUP_CONCAT(f.url_foto) AS fotos,
               c.latitud, c.longitud,
               u.id, u.name, u.email, u.telefono
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
        LEFT JOIN usuario u ON d.id_usuario = u.id
        WHERE d.id_departamento = %s
        GROUP BY d.id_departamento, u.id, u.name, u.email, u.telefono
    ''', (property_id,))
    data = cursor.fetchone()

    if not data:
        cursor.close()
        flash('Propiedad no encontrada.', 'danger')
        return redirect(url_for('main.home'))

    departamento = {
        "id": data[0], "titulo": data[1], "descripcion": data[2],
        "tipo_publicacion": data[3], "precio": data[4], "moneda": data[5],
        "ambientes": data[6], "dormitorios": data[7], "banos": data[8],
        "superficie": data[9], "direccion": data[10], "rol_inmo_dir": data[11],
        "fotos": data[12].split(',') if data[12] else [],
        "latitud": float(data[13]) if data[13] else 0.0,
        "longitud": float(data[14]) if data[14] else 0.0,
        "propietario_id": data[15]
    }
    publicador = {
        "id": data[15], "nombre": data[16],
        "email": data[17], "telefono": data[18]
    }

    cursor.execute('''
        SELECT r.id_resena, r.puntaje, r.comentario, r.fecha_calificacion,
               u.name, r.id_usuario_calificador
        FROM resena r
        JOIN usuario u ON r.id_usuario_calificador = u.id
        WHERE r.id_departamento = %s
        ORDER BY r.fecha_calificacion DESC
    ''', (property_id,))
    resenas = [{
        "id_resena": r[0], "puntaje": r[1], "comentario": r[2],
        "fecha_calificacion": r[3], "calificador_nombre": r[4],
        "id_usuario_calificador": r[5]
    } for r in cursor.fetchall()]

    current_user_id = session.get('user_id')
    user_has_reviewed = False
    user_review_id = None
    favoritos = []

    if current_user_id:
        for resena in resenas:
            if resena['id_usuario_calificador'] == current_user_id:
                user_has_reviewed = True
                user_review_id = resena['id_resena']
                break
        cursor.execute('SELECT id_departamento FROM favorito WHERE id_usuario = %s',
                       (current_user_id,))
        favoritos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return render_template('viewProperty.html',
                           departamento=departamento, publicador=publicador,
                           resenas=resenas, resena_form=ResenaForm(),
                           edit_resena_form=EditResenaForm(),
                           current_user_id=current_user_id,
                           user_has_reviewed=user_has_reviewed,
                           user_review_id=user_review_id,
                           is_authenticated='user_id' in session,
                           favoritos=favoritos)


@deptos_bp.route('/publish_depto', methods=['GET', 'POST'])
def publish_depto():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('auth.login'))

    form = PublishDeptoForm()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.close()
    form.localidad.choices = [(str(id_loc), nombre) for id_loc, nombre in localidades]

    if form.validate_on_submit():
        try:
            latitud = request.form.get('latitud')
            longitud = request.form.get('longitud')
            if not latitud or not longitud:
                flash('Seleccioná una ubicación en el mapa.', 'danger')
                return render_template('publish_depto.html', form=form)

            valid_photos = [p for p in request.files.getlist(form.photos.name)
                            if p and p.filename]
            if not (1 <= len(valid_photos) <= 5):
                flash('Debés subir entre 1 y 5 imágenes.', 'danger')
                return render_template('publish_depto.html', form=form)

            price = float(form.price.data.replace('.', '').replace(',', ''))
            user_id = session['user_id']

            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO departamento
                    (id_usuario, id_localidad, titulo, descripcion, tipo_publicacion,
                     precio, moneda, ambientes, dormitorios, banos, superficie,
                     direccion, rol_inmo_dir, fecha_publicacion)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ''', (user_id, form.localidad.data, form.title.data, form.description.data,
                  form.tipo_publicacion.data, price, form.moneda.data,
                  form.ambientes.data, form.dormitorios.data, form.banos.data,
                  form.superficie.data, form.direccion.data, form.rol_inmo_dir.data))
            depto_id = cursor.lastrowid

            cursor.execute(
                'INSERT INTO coordenadas (id_departamento, latitud, longitud) VALUES (%s,%s,%s)',
                (depto_id, latitud, longitud)
            )

            for photo in valid_photos:
                filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
                from flask import current_app
                photo.save(os.path.join(current_app.root_path, 'static', 'image', filename))
                cursor.execute(
                    'INSERT INTO foto (id_departamento, url_foto) VALUES (%s,%s)',
                    (depto_id, filename)
                )

            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('deptos.publication_success'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al publicar: {str(e)}', 'danger')
            return render_template('publish_depto.html', form=form)

    for field, errors in form.errors.items():
        for error in errors:
            label = getattr(form, field).label.text
            flash(f"Error en '{label}': {error}", 'danger')

    return render_template('publish_depto.html', form=form)


@deptos_bp.route('/modify_depto/<int:depto_id>', methods=['GET', 'POST'])
def modify_depto(depto_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.titulo, d.descripcion, d.tipo_publicacion, d.precio, d.moneda,
               d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion,
               d.id_localidad, d.rol_inmo_dir, d.estado,
               GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        WHERE d.id_departamento = %s AND d.id_usuario = %s
        GROUP BY d.id_departamento
    ''', (depto_id, session['user_id']))
    depto_data = cursor.fetchone()

    if not depto_data:
        flash('Departamento no encontrado o sin permisos.', 'danger')
        cursor.close()
        return redirect(url_for('user.user_panel'))

    cursor.execute('SELECT id_localidad, nombre FROM localidad')
    localidades = cursor.fetchall()
    cursor.execute('SELECT latitud, longitud FROM coordenadas WHERE id_departamento = %s', (depto_id,))
    coords = cursor.fetchone()
    cursor.close()

    form = PublishDeptoForm()
    form.localidad.choices = [(str(id_loc), nombre) for id_loc, nombre in localidades]
    form.photos.validators = []

    if request.method == 'GET':
        form.title.data = depto_data[0]
        form.description.data = depto_data[1]
        form.tipo_publicacion.data = depto_data[2]
        form.price.data = f"{int(depto_data[3]):,}".replace(',', '.')
        form.moneda.data = depto_data[4]
        form.ambientes.data = depto_data[5]
        form.dormitorios.data = depto_data[6]
        form.banos.data = depto_data[7]
        form.superficie.data = depto_data[8]
        form.direccion.data = depto_data[9]
        form.localidad.data = str(depto_data[10])
        form.rol_inmo_dir.data = depto_data[11]

    if form.validate_on_submit():
        try:
            price = float(form.price.data.replace('.', '').replace(',', ''))
            cursor = mysql.connection.cursor()
            cursor.execute('''
                UPDATE departamento SET titulo=%s, descripcion=%s, tipo_publicacion=%s,
                    precio=%s, moneda=%s, ambientes=%s, dormitorios=%s, banos=%s,
                    superficie=%s, direccion=%s, id_localidad=%s, rol_inmo_dir=%s, estado=%s
                WHERE id_departamento=%s AND id_usuario=%s
            ''', (form.title.data, form.description.data, form.tipo_publicacion.data,
                  price, form.moneda.data, form.ambientes.data, form.dormitorios.data,
                  form.banos.data, form.superficie.data, form.direccion.data,
                  form.localidad.data, form.rol_inmo_dir.data,
                  request.form.get('estado'), depto_id, session['user_id']))

            lat = request.form.get('latitud')
            lon = request.form.get('longitud')
            if lat and lon:
                cursor.execute(
                    'UPDATE coordenadas SET latitud=%s, longitud=%s WHERE id_departamento=%s',
                    (lat, lon, depto_id)
                )

            new_photos = [p for p in request.files.getlist(form.photos.name)
                          if p and p.filename]
            if new_photos:
                cursor.execute('SELECT COUNT(*) FROM foto WHERE id_departamento=%s', (depto_id,))
                current_count = cursor.fetchone()[0]
                slots = 5 - current_count
                if slots <= 0:
                    flash('Ya tenés el máximo de 5 imágenes.', 'warning')
                else:
                    for photo in new_photos[:slots]:
                        from flask import current_app
                        filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
                        photo.save(os.path.join(current_app.root_path, 'static', 'image', filename))
                        cursor.execute(
                            'INSERT INTO foto (id_departamento, url_foto) VALUES (%s,%s)',
                            (depto_id, filename)
                        )

            mysql.connection.commit()
            cursor.close()
            flash('Departamento actualizado.', 'success')
            return redirect(url_for('user.user_panel'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
        finally:
            if cursor:
                cursor.close()

    current_photos = depto_data[13].split(',') if depto_data[13] else []
    return render_template('modify_depto.html', form=form, depto_id=depto_id,
                           latitud=coords[0] if coords else '',
                           longitud=coords[1] if coords else '',
                           current_photos=current_photos,
                           current_status=depto_data[12])


@deptos_bp.route('/delete_publication/<int:publication_id>', methods=['POST'])
def delete_publication(publication_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM coordenadas WHERE id_departamento=%s', (publication_id,))
        cursor.execute('DELETE FROM foto WHERE id_departamento=%s', (publication_id,))
        cursor.execute('DELETE FROM departamento WHERE id_departamento=%s AND id_usuario=%s',
                       (publication_id, session['user_id']))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('deptos.delete_confirmation'))
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar: {e}', 'danger')
        return redirect(url_for('user.user_panel'))


@deptos_bp.route('/update_status/<int:publication_id>', methods=['POST'])
def update_status(publication_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    new_status = request.form.get('estado')
    valid_states = ['disponible', 'reservado', 'vendido', 'alquilado']
    if not new_status or new_status not in valid_states:
        flash('Estado inválido.', 'danger')
        return redirect(url_for('user.user_panel'))
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE departamento SET estado=%s WHERE id_departamento=%s AND id_usuario=%s',
            (new_status, publication_id, session['user_id'])
        )
        mysql.connection.commit()
        cursor.close()
        flash(f'Estado actualizado a: {new_status}', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('user.user_panel'))


@deptos_bp.route('/delete_photo/<int:depto_id>/<photo_name>', methods=['POST'])
def delete_photo(depto_id, photo_name):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'})
    try:
        from flask import current_app
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT id_departamento FROM departamento WHERE id_departamento=%s AND id_usuario=%s',
            (depto_id, session['user_id'])
        )
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': 'Sin permisos'})
        cursor.execute('DELETE FROM foto WHERE id_departamento=%s AND url_foto=%s',
                       (depto_id, photo_name))
        mysql.connection.commit()
        cursor.close()
        foto_path = os.path.join(current_app.root_path, 'static', 'image', photo_name)
        if os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@deptos_bp.route('/departamento/<int:departamento_id>/add_resena', methods=['POST'])
def add_resena(departamento_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para dejar una reseña.', 'warning')
        return redirect(url_for('auth.login'))

    form = ResenaForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT id_usuario FROM departamento WHERE id_departamento=%s',
                       (departamento_id,))
        owner = cursor.fetchone()
        if owner and owner[0] == user_id:
            flash('No podés reseñar tu propio departamento.', 'danger')
            cursor.close()
            return redirect(url_for('deptos.view_property', property_id=departamento_id))

        cursor.execute(
            'SELECT id_resena FROM resena WHERE id_departamento=%s AND id_usuario_calificador=%s',
            (departamento_id, user_id)
        )
        if cursor.fetchone():
            flash('Ya dejaste una reseña. Podés editarla.', 'info')
            cursor.close()
            return redirect(url_for('deptos.view_property', property_id=departamento_id))

        cursor.execute('''
            INSERT INTO resena (id_departamento, id_usuario_calificador, puntaje, comentario, fecha_calificacion)
            VALUES (%s,%s,%s,%s,NOW())
        ''', (departamento_id, user_id, form.puntaje.data, form.comentario.data))
        resena_id = cursor.lastrowid

        if owner:
            cursor.execute('SELECT name FROM usuario WHERE id=%s', (user_id,))
            nombre = cursor.fetchone()
            cursor.execute('SELECT titulo FROM departamento WHERE id_departamento=%s',
                           (departamento_id,))
            titulo = cursor.fetchone()
            if nombre and titulo:
                cursor.execute('''
                    INSERT INTO notificaciones
                        (id_usuario_receptor, tipo_notificacion, mensaje,
                         id_departamento_ref, id_resena_ref, fecha_envio, leida)
                    VALUES (%s,'NUEVA_RESENA',%s,%s,%s,NOW(),0)
                ''', (owner[0],
                      f"'{nombre[0]}' dejó una reseña en '{titulo[0]}'.",
                      departamento_id, resena_id))

        mysql.connection.commit()
        cursor.close()
        flash('Reseña agregada.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en '{getattr(form, field).label.text}': {error}", 'danger')

    return redirect(url_for('deptos.view_property', property_id=departamento_id))


@deptos_bp.route('/resena/<int:resena_id>/edit', methods=['GET', 'POST'])
def edit_resena(resena_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT id_departamento, id_usuario_calificador, puntaje, comentario FROM resena WHERE id_resena=%s',
        (resena_id,)
    )
    resena = cursor.fetchone()
    if not resena or resena[1] != session['user_id']:
        flash('Sin permisos para editar esta reseña.', 'danger')
        cursor.close()
        return redirect(url_for('main.home'))

    form = EditResenaForm(request.form)
    if request.method == 'POST' and form.validate():
        cursor.execute(
            'UPDATE resena SET puntaje=%s, comentario=%s, fecha_calificacion=NOW() WHERE id_resena=%s',
            (form.puntaje.data, form.comentario.data, resena_id)
        )
        mysql.connection.commit()
        cursor.close()
        flash('Reseña actualizada.', 'success')
        return redirect(url_for('deptos.view_property', property_id=resena[0]))

    if request.method == 'GET':
        form.puntaje.data = str(resena[2])
        form.comentario.data = resena[3]

    cursor.close()
    return render_template('edit_resena_modal_content.html', form=form,
                           resena_id=resena_id, property_id=resena[0])


@deptos_bp.route('/resena/<int:resena_id>/delete', methods=['POST'])
def delete_resena(resena_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401

    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT id_departamento, id_usuario_calificador FROM resena WHERE id_resena=%s',
        (resena_id,)
    )
    resena = cursor.fetchone()
    if not resena:
        cursor.close()
        return jsonify({'success': False, 'message': 'No encontrada'}), 404
    if resena[1] != session['user_id']:
        cursor.close()
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    try:
        cursor.execute('DELETE FROM notificaciones WHERE id_resena_ref=%s', (resena_id,))
        cursor.execute('DELETE FROM resena WHERE id_resena=%s', (resena_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True,
                        'redirect_url': url_for('deptos.view_property',
                                                property_id=resena[0])})
    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'success': False, 'message': str(e)}), 500


@deptos_bp.route('/delete_confirmation')
def delete_confirmation():
    return render_template('delete_confirmation.html')


@deptos_bp.route('/publication_success')
def publication_success():
    return render_template('publication_success.html')