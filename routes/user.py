from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.security import generate_password_hash
from flask_login import login_required

from extensions import db
from models import Usuario, Departamento, Favorito, Notificacion
from forms import EditProfileForm, PublishDeptoForm
from routes.auth import _verify_password

user_bp = Blueprint('user', __name__)


@user_bp.route('/user_panel')
def user_panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)

    user = Usuario.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    pagination = Departamento.query.filter_by(id_usuario=user_id)\
        .paginate(page=page, per_page=2, error_out=False)

    notificaciones = [{
        "id": n.id_notificacion, "tipo": n.tipo_notificacion,
        "mensaje": n.mensaje, "id_departamento_ref": n.id_departamento_ref,
        "id_resena_ref": n.id_resena_ref, "fecha_envio": n.fecha_envio,
        "leida": n.leida
    } for n in Notificacion.query.filter_by(id_usuario_receptor=user_id)
                      .order_by(Notificacion.fecha_envio.desc()).all()]

    mis_publicaciones = []
    for d in pagination.items:
        fotos = [f.url_foto for f in d.fotos]
        lat = float(d.coordenadas.latitud) if d.coordenadas else ''
        lng = float(d.coordenadas.longitud) if d.coordenadas else ''
        mis_publicaciones.append((
            d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion,
            d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos,
            d.superficie, d.direccion, d.rol_inmo_dir, d.estado, fotos, lat, lng
        ))

    user_data = (user.name, user.email, user.fecha_registro, user.telefono)
    return render_template('user_panel.html', user_data=user_data,
                           mis_publicaciones=mis_publicaciones,
                           form=PublishDeptoForm(),
                           notificaciones=notificaciones,
                           page=page, total_pages=pagination.pages)


@user_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = Usuario.query.get(session['user_id'])
    if not user:
        return redirect(url_for('main.home'))

    edit_count = user.ediciones_ultimos_dos_dias or 0
    now = datetime.now()
    puede_modificar = True

    if user.fecha_ultima_modificacion:
        last = user.fecha_ultima_modificacion
        if now - last > timedelta(days=2):
            edit_count = 0
        if edit_count >= 2 and now - last <= timedelta(days=2):
            puede_modificar = False

    form = EditProfileForm(original_username=user.name)
    if request.method == 'GET':
        form.username.data = user.name
        form.email.data = user.email
        form.telefono.data = user.telefono or ''

    if form.validate_on_submit() and puede_modificar:
        if form.password.data:
            if not form.current_password.data:
                flash('Debés ingresar tu contraseña actual.', 'danger')
                return render_template('edit_profile.html', form=form,
                                       puede_modificar=puede_modificar)
            if not _verify_password(user.password, form.current_password.data):
                flash('La contraseña actual es incorrecta.', 'danger')
                return render_template('edit_profile.html', form=form,
                                       puede_modificar=puede_modificar)
            user.password = generate_password_hash(form.password.data)

        user.name = form.username.data
        user.email = form.email.data
        user.telefono = form.telefono.data
        user.fecha_ultima_modificacion = now
        user.ediciones_ultimos_dos_dias = edit_count + 1
        db.session.commit()
        session['user_name'] = user.name
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('user.user_panel'))
    elif not puede_modificar and request.method == 'POST':
        flash('Solo podés editar tu perfil 2 veces cada 2 días.', 'warning')

    return render_template('edit_profile.html', form=form,
                           puede_modificar=puede_modificar)


@user_bp.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    page = request.args.get('page', 1, type=int)
    pagination = Favorito.query.filter_by(id_usuario=session['user_id'])\
        .paginate(page=page, per_page=6, error_out=False)

    favoritos = []
    for f in pagination.items:
        d = f.departamento
        fotos = [foto.url_foto for foto in d.fotos]
        favoritos.append((
            d.id_departamento, d.titulo, d.descripcion, d.precio,
            d.moneda, d.ambientes, d.dormitorios, d.banos,
            d.superficie, d.direccion, d.rol_inmo_dir, fotos
        ))
    return render_template('favorites.html', favoritos=favoritos,
                           page=page, total_pages=pagination.pages)


@user_bp.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    try:
        fav = Favorito(id_usuario=session['user_id'],
                       id_departamento=request.form['property_id'])
        db.session.add(fav)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@user_bp.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    try:
        Favorito.query.filter_by(
            id_usuario=session['user_id'],
            id_departamento=request.form['property_id']
        ).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@user_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    notifs = Notificacion.query.filter_by(id_usuario_receptor=session['user_id'])\
        .order_by(Notificacion.fecha_envio.desc()).all()
    notificaciones = [{
        "id": n.id_notificacion, "tipo": n.tipo_notificacion,
        "mensaje": n.mensaje, "id_departamento_ref": n.id_departamento_ref,
        "id_resena_ref": n.id_resena_ref,
        "fecha_envio": n.fecha_envio.strftime('%Y-%m-%d %H:%M') if n.fecha_envio else "—",
        "leida": n.leida
    } for n in notifs]
    return render_template('notifications.html', notificaciones=notificaciones)


@user_bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    n = Notificacion.query.filter_by(id_notificacion=notification_id,
                                    id_usuario_receptor=session['user_id']).first()
    if n:
        n.leida = True
        db.session.commit()
    return jsonify({'success': True})


@user_bp.route('/notifications/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    try:
        n = Notificacion.query.filter_by(id_notificacion=notification_id,
                                        id_usuario_receptor=session['user_id']).first()
        if n and n.id_resena_ref:
            Notificacion.query.filter_by(id_resena_ref=n.id_resena_ref).delete()
            from models import Resena
            Resena.query.filter_by(id_resena=n.id_resena_ref).delete()
        elif n:
            db.session.delete(n)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500