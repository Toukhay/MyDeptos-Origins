import os
import uuid
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify, current_app)
from werkzeug.utils import secure_filename

from extensions import db
from models import Departamento, Foto, Coordenada, Localidad, Favorito, Resena, Notificacion, Usuario
from forms import PublishDeptoForm, ResenaForm, EditResenaForm

deptos_bp = Blueprint('deptos', __name__)


def _save_photo(photo, app):
    filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
    path = os.path.join(app.root_path, 'static', 'image', filename)
    photo.save(path)
    return filename


@deptos_bp.route('/viewProperty/<int:property_id>', methods=['GET', 'POST'])
def view_property(property_id):
    depto = Departamento.query.get(property_id)
    if not depto:
        flash('Propiedad no encontrada.', 'danger')
        return redirect(url_for('main.home'))

    departamento = {
        "id": depto.id_departamento,
        "titulo": depto.titulo,
        "descripcion": depto.descripcion,
        "tipo_publicacion": depto.tipo_publicacion,
        "precio": depto.precio,
        "moneda": depto.moneda,
        "ambientes": depto.ambientes,
        "dormitorios": depto.dormitorios,
        "banos": depto.banos,
        "superficie": depto.superficie,
        "direccion": depto.direccion,
        "rol_inmo_dir": depto.rol_inmo_dir,
        "fotos": [f.url_foto for f in depto.fotos],
        "latitud": float(depto.coordenadas.latitud) if depto.coordenadas else 0.0,
        "longitud": float(depto.coordenadas.longitud) if depto.coordenadas else 0.0,
        "propietario_id": depto.id_usuario
    }
    publicador = {
        "id": depto.propietario.id,
        "nombre": depto.propietario.name,
        "email": depto.propietario.email,
        "telefono": depto.propietario.telefono
    }

    resenas = [{
        "id_resena": r.id_resena,
        "puntaje": r.puntaje,
        "comentario": r.comentario,
        "fecha_calificacion": r.fecha_calificacion,
        "calificador_nombre": r.calificador.name,
        "id_usuario_calificador": r.id_usuario_calificador
    } for r in depto.resenas]

    current_user_id = session.get('user_id')
    user_has_reviewed = False
    user_review_id = None
    favoritos = []

    if current_user_id:
        for r in resenas:
            if r['id_usuario_calificador'] == current_user_id:
                user_has_reviewed = True
                user_review_id = r['id_resena']
                break
        favoritos = [f.id_departamento for f in
                     Favorito.query.filter_by(id_usuario=current_user_id).all()]

    return render_template('viewProperty.html',
                           departamento=departamento,
                           publicador=publicador,
                           resenas=resenas,
                           resena_form=ResenaForm(),
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
    form.localidad.choices = [(str(l.id_localidad), l.nombre)
                              for l in Localidad.query.all()]

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

            depto = Departamento(
                id_usuario=session['user_id'],
                id_localidad=form.localidad.data,
                titulo=form.title.data,
                descripcion=form.description.data,
                tipo_publicacion=form.tipo_publicacion.data,
                precio=price,
                moneda=form.moneda.data,
                ambientes=form.ambientes.data,
                dormitorios=form.dormitorios.data,
                banos=form.banos.data,
                superficie=form.superficie.data,
                direccion=form.direccion.data,
                rol_inmo_dir=form.rol_inmo_dir.data
            )
            db.session.add(depto)
            db.session.flush()

            coords = Coordenada(id_departamento=depto.id_departamento,
                                latitud=latitud, longitud=longitud)
            db.session.add(coords)

            for photo in valid_photos:
                filename = _save_photo(photo, current_app._get_current_object())
                db.session.add(Foto(id_departamento=depto.id_departamento,
                                    url_foto=filename))

            db.session.commit()
            return redirect(url_for('deptos.publication_success'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al publicar: {str(e)}', 'danger')
            return render_template('publish_depto.html', form=form)

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en '{getattr(form, field).label.text}': {error}", 'danger')

    return render_template('publish_depto.html', form=form)


@deptos_bp.route('/modify_depto/<int:depto_id>', methods=['GET', 'POST'])
def modify_depto(depto_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    depto = Departamento.query.filter_by(
        id_departamento=depto_id, id_usuario=session['user_id']
    ).first()
    if not depto:
        flash('Departamento no encontrado o sin permisos.', 'danger')
        return redirect(url_for('user.user_panel'))

    form = PublishDeptoForm()
    form.localidad.choices = [(str(l.id_localidad), l.nombre)
                              for l in Localidad.query.all()]
    form.photos.validators = []

    if request.method == 'GET':
        form.title.data = depto.titulo
        form.description.data = depto.descripcion
        form.tipo_publicacion.data = depto.tipo_publicacion
        form.price.data = f"{int(depto.precio):,}".replace(',', '.')
        form.moneda.data = depto.moneda
        form.ambientes.data = depto.ambientes
        form.dormitorios.data = depto.dormitorios
        form.banos.data = depto.banos
        form.superficie.data = depto.superficie
        form.direccion.data = depto.direccion
        form.localidad.data = str(depto.id_localidad)
        form.rol_inmo_dir.data = depto.rol_inmo_dir

    if form.validate_on_submit():
        try:
            depto.titulo = form.title.data
            depto.descripcion = form.description.data
            depto.tipo_publicacion = form.tipo_publicacion.data
            depto.precio = float(form.price.data.replace('.', '').replace(',', ''))
            depto.moneda = form.moneda.data
            depto.ambientes = form.ambientes.data
            depto.dormitorios = form.dormitorios.data
            depto.banos = form.banos.data
            depto.superficie = form.superficie.data
            depto.direccion = form.direccion.data
            depto.id_localidad = form.localidad.data
            depto.rol_inmo_dir = form.rol_inmo_dir.data
            depto.estado = request.form.get('estado', depto.estado)

            lat = request.form.get('latitud')
            lon = request.form.get('longitud')
            if lat and lon and depto.coordenadas:
                depto.coordenadas.latitud = lat
                depto.coordenadas.longitud = lon

            new_photos = [p for p in request.files.getlist(form.photos.name)
                          if p and p.filename]
            if new_photos:
                current_count = len(depto.fotos)
                slots = 5 - current_count
                if slots <= 0:
                    flash('Ya tenés el máximo de 5 imágenes.', 'warning')
                else:
                    for photo in new_photos[:slots]:
                        filename = _save_photo(photo, current_app._get_current_object())
                        db.session.add(Foto(id_departamento=depto_id, url_foto=filename))

            db.session.commit()
            flash('Departamento actualizado.', 'success')
            return redirect(url_for('user.user_panel'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    current_photos = [f.url_foto for f in depto.fotos]
    lat = float(depto.coordenadas.latitud) if depto.coordenadas else ''
    lon = float(depto.coordenadas.longitud) if depto.coordenadas else ''
    return render_template('modify_depto.html', form=form, depto_id=depto_id,
                           latitud=lat, longitud=lon,
                           current_photos=current_photos,
                           current_status=depto.estado)


@deptos_bp.route('/delete_publication/<int:publication_id>', methods=['POST'])
def delete_publication(publication_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    depto = Departamento.query.filter_by(
        id_departamento=publication_id, id_usuario=session['user_id']
    ).first()
    if depto:
        db.session.delete(depto)
        db.session.commit()
    return redirect(url_for('deptos.delete_confirmation'))


@deptos_bp.route('/update_status/<int:publication_id>', methods=['POST'])
def update_status(publication_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    valid_states = ['disponible', 'reservado', 'vendido', 'alquilado']
    new_status = request.form.get('estado')
    if not new_status or new_status not in valid_states:
        flash('Estado inválido.', 'danger')
        return redirect(url_for('user.user_panel'))
    depto = Departamento.query.filter_by(
        id_departamento=publication_id, id_usuario=session['user_id']
    ).first()
    if depto:
        depto.estado = new_status
        db.session.commit()
        flash(f'Estado actualizado a: {new_status}', 'success')
    return redirect(url_for('user.user_panel'))


@deptos_bp.route('/delete_photo/<int:depto_id>/<photo_name>', methods=['POST'])
def delete_photo(depto_id, photo_name):
    if 'user_id' not in session:
        return jsonify({'success': False})
    depto = Departamento.query.filter_by(
        id_departamento=depto_id, id_usuario=session['user_id']
    ).first()
    if not depto:
        return jsonify({'success': False, 'message': 'Sin permisos'})
    foto = Foto.query.filter_by(id_departamento=depto_id, url_foto=photo_name).first()
    if foto:
        db.session.delete(foto)
        db.session.commit()
        path = os.path.join(current_app.root_path, 'static', 'image', photo_name)
        if os.path.exists(path):
            os.remove(path)
    return jsonify({'success': True})


@deptos_bp.route('/departamento/<int:departamento_id>/add_resena', methods=['POST'])
def add_resena(departamento_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    form = ResenaForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        depto = Departamento.query.get(departamento_id)

        if depto.id_usuario == user_id:
            flash('No podés reseñar tu propio departamento.', 'danger')
            return redirect(url_for('deptos.view_property', property_id=departamento_id))

        existing = Resena.query.filter_by(
            id_departamento=departamento_id,
            id_usuario_calificador=user_id
        ).first()
        if existing:
            flash('Ya dejaste una reseña. Podés editarla.', 'info')
            return redirect(url_for('deptos.view_property', property_id=departamento_id))

        resena = Resena(
            id_departamento=departamento_id,
            id_usuario_calificador=user_id,
            puntaje=form.puntaje.data,
            comentario=form.comentario.data
        )
        db.session.add(resena)
        db.session.flush()

        calificador = Usuario.query.get(user_id)
        notif = Notificacion(
            id_usuario_receptor=depto.id_usuario,
            tipo_notificacion='NUEVA_RESENA',
            mensaje=f"'{calificador.name}' dejó una reseña en '{depto.titulo}'.",
            id_departamento_ref=departamento_id,
            id_resena_ref=resena.id_resena
        )
        db.session.add(notif)
        db.session.commit()
        flash('Reseña agregada.', 'success')

    return redirect(url_for('deptos.view_property', property_id=departamento_id))


@deptos_bp.route('/resena/<int:resena_id>/edit', methods=['GET', 'POST'])
def edit_resena(resena_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    resena = Resena.query.get(resena_id)
    if not resena or resena.id_usuario_calificador != session['user_id']:
        flash('Sin permisos.', 'danger')
        return redirect(url_for('main.home'))

    form = EditResenaForm(request.form)
    if request.method == 'POST' and form.validate():
        resena.puntaje = form.puntaje.data
        resena.comentario = form.comentario.data
        db.session.commit()
        flash('Reseña actualizada.', 'success')
        return redirect(url_for('deptos.view_property',
                                property_id=resena.id_departamento))
    if request.method == 'GET':
        form.puntaje.data = str(resena.puntaje)
        form.comentario.data = resena.comentario

    return render_template('edit_resena_modal_content.html', form=form,
                           resena_id=resena_id,
                           property_id=resena.id_departamento)


@deptos_bp.route('/resena/<int:resena_id>/delete', methods=['POST'])
def delete_resena(resena_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    resena = Resena.query.get(resena_id)
    if not resena:
        return jsonify({'success': False}), 404
    if resena.id_usuario_calificador != session['user_id']:
        return jsonify({'success': False}), 403
    property_id = resena.id_departamento
    try:
        Notificacion.query.filter_by(id_resena_ref=resena_id).delete()
        db.session.delete(resena)
        db.session.commit()
        return jsonify({'success': True,
                        'redirect_url': url_for('deptos.view_property',
                                                property_id=property_id)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@deptos_bp.route('/delete_confirmation')
def delete_confirmation():
    return render_template('delete_confirmation.html')


@deptos_bp.route('/publication_success')
def publication_success():
    return render_template('publication_success.html')