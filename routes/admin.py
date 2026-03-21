import os
import uuid
from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from extensions import mysql

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión como administrador.', 'warning')
            return redirect(url_for('auth.login'))
        cur = mysql.connection.cursor()
        cur.execute("SELECT rol FROM usuario WHERE id=%s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        if not user or user[0] != 'admin':
            flash('Acceso restringido a administradores.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin_panel')
@admin_required
def admin_panel():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, telefono, rol FROM usuario")
    usuarios = cur.fetchall()
    cur.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda,
               d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion,
               d.rol_inmo_dir, d.estado, u.name,
               GROUP_CONCAT(f.url_foto) AS fotos
        FROM departamento d
        JOIN usuario u ON d.id_usuario = u.id
        LEFT JOIN foto f ON d.id_departamento = f.id_departamento
        GROUP BY d.id_departamento
    ''')
    departamentos = cur.fetchall()
    cur.close()
    return render_template('admin_panel.html', usuarios=usuarios,
                           departamentos=departamentos)


@admin_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, telefono, rol FROM usuario WHERE id=%s", (user_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin.admin_panel'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        new_password = request.form.get('new_password')
        rol = 'admin' if request.form.get('rol') == 'on' else 'user'
        try:
            if new_password and new_password.strip():
                hashed = generate_password_hash(new_password)
                cur.execute(
                    "UPDATE usuario SET name=%s, email=%s, telefono=%s, rol=%s, password=%s WHERE id=%s",
                    (name, email, telefono, rol, hashed, user_id)
                )
            else:
                cur.execute(
                    "UPDATE usuario SET name=%s, email=%s, telefono=%s, rol=%s WHERE id=%s",
                    (name, email, telefono, rol, user_id)
                )
            mysql.connection.commit()
            cur.close()
            flash('Usuario actualizado.', 'success')
            return redirect(url_for('admin.admin_panel'))
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('admin.admin_panel'))

    cur.close()
    return render_template('admin_edit_user.html', user=user)


@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM favorito WHERE id_usuario=%s", (user_id,))
    cur.execute("DELETE FROM resena WHERE id_usuario_calificador=%s", (user_id,))
    cur.execute("DELETE FROM notificaciones WHERE id_usuario_receptor=%s", (user_id,))
    cur.execute("DELETE FROM configuracion_usuario WHERE id_usuario=%s", (user_id,))
    cur.execute("DELETE FROM usuario WHERE id=%s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado.', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/depto/<int:depto_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_depto(depto_id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda,
               d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion,
               d.rol_inmo_dir, d.estado, c.latitud, c.longitud
        FROM departamento d
        LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
        WHERE d.id_departamento = %s
    ''', (depto_id,))
    depto = cur.fetchone()
    if not depto:
        cur.close()
        flash('Departamento no encontrado.', 'danger')
        return redirect(url_for('admin.admin_panel'))

    cur.execute('SELECT url_foto FROM foto WHERE id_departamento=%s', (depto_id,))
    current_photos = [r[0] for r in cur.fetchall()]
    precio_formateado = f"{int(depto[3]):,}".replace(',', '.')
    latitud = depto[12] if depto[12] else -27.485104
    longitud = depto[13] if depto[13] else -55.119835

    if request.method == 'POST':
        try:
            precio_str = request.form.get('precio', '')
            precio = float(precio_str.replace('.', '').replace(',', '')) if precio_str else 0
            cur.execute('''
                UPDATE departamento SET titulo=%s, descripcion=%s, precio=%s, moneda=%s,
                       ambientes=%s, dormitorios=%s, banos=%s, superficie=%s,
                       direccion=%s, rol_inmo_dir=%s, estado=%s
                WHERE id_departamento=%s
            ''', (request.form.get('titulo'), request.form.get('descripcion'),
                  precio, request.form.get('moneda'),
                  request.form.get('ambientes'), request.form.get('dormitorios'),
                  request.form.get('banos'), request.form.get('superficie'),
                  request.form.get('direccion'), request.form.get('rol_inmo_dir'),
                  request.form.get('estado'), depto_id))

            lat = request.form.get('latitud')
            lon = request.form.get('longitud')
            if lat and lon:
                cur.execute('SELECT id_departamento FROM coordenadas WHERE id_departamento=%s',
                            (depto_id,))
                if cur.fetchone():
                    cur.execute('UPDATE coordenadas SET latitud=%s, longitud=%s WHERE id_departamento=%s',
                                (lat, lon, depto_id))
                else:
                    cur.execute('INSERT INTO coordenadas (id_departamento, latitud, longitud) VALUES (%s,%s,%s)',
                                (depto_id, lat, lon))

            if 'new_photos' in request.files:
                new_photos = [p for p in request.files.getlist('new_photos')
                              if p and p.filename and p.filename.strip()]
                if new_photos:
                    cur.execute('SELECT COUNT(*) FROM foto WHERE id_departamento=%s', (depto_id,))
                    count = cur.fetchone()[0]
                    slots = 5 - count
                    from flask import current_app
                    for photo in new_photos[:slots]:
                        filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
                        photo.save(os.path.join(current_app.root_path, 'static', 'image', filename))
                        cur.execute('INSERT INTO foto (id_departamento, url_foto) VALUES (%s,%s)',
                                    (depto_id, filename))

            mysql.connection.commit()
            cur.close()
            flash('Departamento actualizado.', 'success')
            return redirect(url_for('admin.admin_panel'))
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('admin.admin_panel'))

    cur.close()
    return render_template('admin_edit_depto.html', depto=depto,
                           precio_formateado=precio_formateado,
                           latitud=latitud, longitud=longitud,
                           current_photos=current_photos)


@admin_bp.route('/admin/depto/<int:depto_id>/delete', methods=['POST'])
@admin_required
def admin_delete_depto(depto_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM resena WHERE id_departamento=%s", (depto_id,))
    cur.execute("DELETE FROM favorito WHERE id_departamento=%s", (depto_id,))
    cur.execute("DELETE FROM foto WHERE id_departamento=%s", (depto_id,))
    cur.execute("DELETE FROM coordenadas WHERE id_departamento=%s", (depto_id,))
    cur.execute("DELETE FROM departamento WHERE id_departamento=%s", (depto_id,))
    mysql.connection.commit()
    cur.close()
    flash('Departamento eliminado.', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/foto/<int:depto_id>/<foto_nombre>/delete', methods=['POST'])
@admin_required
def admin_delete_foto(depto_id, foto_nombre):
    try:
        from flask import current_app
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM foto WHERE id_departamento=%s AND url_foto=%s',
                    (depto_id, foto_nombre))
        mysql.connection.commit()
        cur.close()
        foto_path = os.path.join(current_app.root_path, 'static', 'image', foto_nombre)
        if os.path.exists(foto_path):
            os.remove(foto_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})