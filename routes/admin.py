import os
import uuid
from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify, current_app)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from extensions import db
from models import Usuario, Departamento, Foto, Coordenada, Resena, Favorito, Notificacion

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión como administrador.', 'warning')
            return redirect(url_for('auth.login'))
        user = Usuario.query.get(session['user_id'])
        if not user or user.rol != 'admin':
            flash('Acceso restringido a administradores.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin_panel')
@admin_required
def admin_panel():
    usuarios = Usuario.query.all()
    departamentos = Departamento.query.all()
    return render_template('admin_panel.html',
                           usuarios=usuarios,
                           departamentos=departamentos)


@admin_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = Usuario.query.get(user_id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin.admin_panel'))

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.telefono = request.form.get('telefono')
        user.rol = 'admin' if request.form.get('rol') == 'on' else 'user'
        new_password = request.form.get('new_password')
        if new_password and new_password.strip():
            user.password = generate_password_hash(new_password)
        try:
            db.session.commit()
            flash('Usuario actualizado.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin.admin_panel'))

    return render_template('admin_edit_user.html', user=user)


@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = Usuario.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado.', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/depto/<int:depto_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_depto(depto_id):
    depto = Departamento.query.get(depto_id)
    if not depto:
        flash('Departamento no encontrado.', 'danger')
        return redirect(url_for('admin.admin_panel'))

    current_photos = [f.url_foto for f in depto.fotos]
    precio_formateado = f"{int(depto.precio):,}".replace(',', '.')
    lat = float(depto.coordenadas.latitud) if depto.coordenadas else -27.485104
    lon = float(depto.coordenadas.longitud) if depto.coordenadas else -55.119835

    if request.method == 'POST':
        try:
            precio_str = request.form.get('precio', '')
            depto.titulo = request.form.get('titulo')
            depto.descripcion = request.form.get('descripcion')
            depto.precio = float(precio_str.replace('.', '').replace(',', '')) if precio_str else 0
            depto.moneda = request.form.get('moneda')
            depto.ambientes = request.form.get('ambientes')
            depto.dormitorios = request.form.get('dormitorios')
            depto.banos = request.form.get('banos')
            depto.superficie = request.form.get('superficie')
            depto.direccion = request.form.get('direccion')
            depto.rol_inmo_dir = request.form.get('rol_inmo_dir')
            depto.estado = request.form.get('estado')

            new_lat = request.form.get('latitud')
            new_lon = request.form.get('longitud')
            if new_lat and new_lon:
                if depto.coordenadas:
                    depto.coordenadas.latitud = new_lat
                    depto.coordenadas.longitud = new_lon
                else:
                    db.session.add(Coordenada(id_departamento=depto_id,
                                              latitud=new_lat, longitud=new_lon))

            if 'new_photos' in request.files:
                new_photos = [p for p in request.files.getlist('new_photos')
                              if p and p.filename and p.filename.strip()]
                slots = 5 - len(depto.fotos)
                for photo in new_photos[:slots]:
                    filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
                    photo.save(os.path.join(current_app.root_path, 'static', 'image', filename))
                    db.session.add(Foto(id_departamento=depto_id, url_foto=filename))

            db.session.commit()
            flash('Departamento actualizado.', 'success')
            return redirect(url_for('admin.admin_panel'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('admin.admin_panel'))

    return render_template('admin_edit_depto.html', depto=depto,
                           precio_formateado=precio_formateado,
                           latitud=lat, longitud=lon,
                           current_photos=current_photos)


@admin_bp.route('/admin/depto/<int:depto_id>/delete', methods=['POST'])
@admin_required
def admin_delete_depto(depto_id):
    depto = Departamento.query.get(depto_id)
    if depto:
        db.session.delete(depto)
        db.session.commit()
        flash('Departamento eliminado.', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/foto/<int:depto_id>/<foto_nombre>/delete', methods=['POST'])
@admin_required
def admin_delete_foto(depto_id, foto_nombre):
    try:
        foto = Foto.query.filter_by(id_departamento=depto_id,
                                    url_foto=foto_nombre).first()
        if foto:
            db.session.delete(foto)
            db.session.commit()
        path = os.path.join(current_app.root_path, 'static', 'image', foto_nombre)
        if os.path.exists(path):
            os.remove(path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})