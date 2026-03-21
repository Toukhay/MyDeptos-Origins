from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

from extensions import mysql
from forms import EditProfileForm
from routes.auth import _verify_password

user_bp = Blueprint('user', __name__)


@user_bp.route('/user_panel')
def user_panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    page = int(request.args.get('page', 1))
    per_page = 2
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT name, email, fecha_registro, telefono FROM usuario WHERE id = %s', (user_id,))
        user_data = cur.fetchone()
        cur.execute('''
            SELECT d.id_departamento, d.titulo, d.descripcion, d.tipo_publicacion,
                   d.precio, d.moneda, d.ambientes, d.dormitorios, d.banos,
                   d.superficie, d.direccion, d.rol_inmo_dir, d.estado,
                   GROUP_CONCAT(f.url_foto) AS fotos, c.latitud, c.longitud
            FROM departamento d
            LEFT JOIN foto f ON d.id_departamento = f.id_departamento
            LEFT JOIN coordenadas c ON d.id_departamento = c.id_departamento
            WHERE d.id_usuario = %s
            GROUP BY d.id_departamento
            LIMIT %s OFFSET %s
        ''', (user_id, per_page, offset))
        mis_publicaciones_data = cur.fetchall()

        cur.execute('SELECT COUNT(*) FROM departamento WHERE id_usuario = %s', (user_id,))
        total = cur.fetchone()[0]
        total_pages = (total + per_page - 1) // per_page

        cur.execute('''
            SELECT id_notificacion, tipo_notificacion, mensaje, id_departamento_ref,
                   id_resena_ref, fecha_envio, leida
            FROM notificaciones WHERE id_usuario_receptor = %s
            ORDER BY fecha_envio DESC
        ''', (user_id,))
        notificaciones_data = cur.fetchall()
    except Exception as e:
        flash(f'Error al cargar datos: {e}', 'danger')
        cur.close()
        return redirect(url_for('main.home'))
    finally:
        cur.close()

    mis_publicaciones = [
        (id_dep, titulo, desc, tipo, precio, moneda, amb, dorm, ban, sup,
         dir_, rol, estado, fotos.split(',') if fotos else [], lat, lng)
        for id_dep, titulo, desc, tipo, precio, moneda, amb, dorm, ban, sup,
            dir_, rol, estado, fotos, lat, lng in mis_publicaciones_data
    ]
    notificaciones = [
        {"id": r[0], "tipo": r[1], "mensaje": r[2], "id_departamento_ref": r[3],
         "id_resena_ref": r[4], "fecha_envio": r[5], "leida": r[6]}
        for r in notificaciones_data
    ]

    from forms import PublishDeptoForm
    form = PublishDeptoForm()
    return render_template('user_panel.html', user_data=user_data,
                           mis_publicaciones=mis_publicaciones, form=form,
                           notificaciones=notificaciones, page=page,
                           total_pages=total_pages)


@user_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT name, email, telefono, fecha_ultima_modificacion, ediciones_ultimos_dos_dias FROM usuario WHERE id = %s",
        (user_id,)
    )
    user = cur.fetchone()
    cur.close()
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.home'))

    last_edit = user[3]
    edit_count = user[4] if user[4] is not None else 0
    now = datetime.now()
    puede_modificar = True

    if last_edit:
        last_edit_dt = last_edit if isinstance(last_edit, datetime) else datetime.strptime(str(last_edit), "%Y-%m-%d %H:%M:%S")
        if now - last_edit_dt > timedelta(days=2):
            edit_count = 0
        if edit_count >= 2 and now - last_edit_dt <= timedelta(days=2):
            puede_modificar = False

    form = EditProfileForm(original_username=user[0])
    if request.method == 'GET':
        form.username.data = user[0]
        form.email.data = user[1]
        form.telefono.data = user[2] or ''

    if form.validate_on_submit() and puede_modificar:
        new_username = form.username.data or user[0]
        new_email = form.email.data or user[1]
        new_telefono = form.telefono.data or ''
        new_password = form.password.data
        current_password = form.current_password.data

        if new_password:
            if not current_password:
                flash('Debés ingresar tu contraseña actual para cambiarla.', 'danger')
                return render_template('edit_profile.html', form=form, puede_modificar=puede_modificar)
            cur = mysql.connection.cursor()
            cur.execute("SELECT password FROM usuario WHERE id = %s", (user_id,))
            stored = cur.fetchone()
            cur.close()
            if not stored or not _verify_password(stored[0], current_password):
                flash('La contraseña actual es incorrecta.', 'danger')
                return render_template('edit_profile.html', form=form, puede_modificar=puede_modificar)
            hashed = generate_password_hash(new_password)
            cur = mysql.connection.cursor()
            cur.execute(
                'UPDATE usuario SET name=%s, email=%s, password=%s, telefono=%s, fecha_ultima_modificacion=%s, ediciones_ultimos_dos_dias=%s WHERE id=%s',
                (new_username, new_email, hashed, new_telefono, now, edit_count + 1, user_id)
            )
            mysql.connection.commit()
            cur.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute(
                'UPDATE usuario SET name=%s, email=%s, telefono=%s, fecha_ultima_modificacion=%s, ediciones_ultimos_dos_dias=%s WHERE id=%s',
                (new_username, new_email, new_telefono, now, edit_count + 1, user_id)
            )
            mysql.connection.commit()
            cur.close()

        session['user_name'] = new_username
        flash('Perfil actualizado con éxito', 'success')
        return redirect(url_for('user.user_panel'))
    elif not puede_modificar and request.method == 'POST':
        flash('Solo podés editar tu perfil 2 veces cada 2 días.', 'warning')

    return render_template('edit_profile.html', form=form, puede_modificar=puede_modificar)


@user_bp.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    page = int(request.args.get('page', 1))
    per_page = 6
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT d.id_departamento, d.titulo, d.descripcion, d.precio, d.moneda,
               d.ambientes, d.dormitorios, d.banos, d.superficie, d.direccion,
               d.rol_inmo_dir, GROUP_CONCAT(fo.url_foto SEPARATOR ',') AS fotos
        FROM favorito f
        JOIN departamento d ON f.id_departamento = d.id_departamento
        LEFT JOIN foto fo ON d.id_departamento = fo.id_departamento
        WHERE f.id_usuario = %s
        GROUP BY d.id_departamento
        LIMIT %s OFFSET %s
    ''', (user_id, per_page, offset))
    favoritos_data = cursor.fetchall()

    cursor.execute('''
        SELECT COUNT(*) FROM favorito f
        JOIN departamento d ON f.id_departamento = d.id_departamento
        WHERE f.id_usuario = %s
    ''', (user_id,))
    total = cursor.fetchone()[0]
    cursor.close()
    total_pages = (total + per_page - 1) // per_page

    favoritos = [
        (id_dep, titulo, desc, precio, moneda, amb, dorm, ban, sup, dir_, rol,
         fotos.split(',') if fotos else [])
        for id_dep, titulo, desc, precio, moneda, amb, dorm, ban, sup, dir_, rol, fotos in favoritos_data
    ]
    return render_template('favorites.html', favoritos=favoritos,
                           page=page, total_pages=total_pages)


@user_bp.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO favorito (id_usuario, id_departamento, fecha_agregado) VALUES (%s, %s, NOW())',
            (session['user_id'], request.form['property_id'])
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@user_bp.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'DELETE FROM favorito WHERE id_usuario = %s AND id_departamento = %s',
            (session['user_id'], request.form['property_id'])
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@user_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT id_notificacion, tipo_notificacion, mensaje, id_departamento_ref,
                   id_resena_ref, fecha_envio, leida
            FROM notificaciones WHERE id_usuario_receptor = %s
            ORDER BY fecha_envio DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        cursor.close()
    except Exception as e:
        flash('Error al cargar notificaciones.', 'danger')
        rows = []

    notificaciones = []
    for row in rows:
        fecha = row[5].strftime('%Y-%m-%d %H:%M') if isinstance(row[5], datetime) else "—"
        notificaciones.append({
            "id": row[0], "tipo": row[1], "mensaje": row[2],
            "id_departamento_ref": row[3], "id_resena_ref": row[4],
            "fecha_envio": fecha, "leida": row[6]
        })
    return render_template('notifications.html', notificaciones=notificaciones)


@user_bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE notificaciones SET leida=1 WHERE id_notificacion=%s AND id_usuario_receptor=%s AND leida=0",
        (notification_id, session['user_id'])
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({'success': True})


@user_bp.route('/notifications/mark_all_read', methods=['POST'])
def mark_all_notifications_read():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE notificaciones SET leida=1 WHERE id_usuario_receptor=%s AND leida=0",
        (session['user_id'],)
    )
    mysql.connection.commit()
    cursor.close()
    flash('Todas las notificaciones marcadas como leídas.', 'success')
    return redirect(url_for('user.notifications'))


@user_bp.route('/notifications/delete/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id_resena_ref FROM notificaciones WHERE id_notificacion=%s AND id_usuario_receptor=%s",
            (notification_id, user_id)
        )
        res = cursor.fetchone()
        if res and res[0]:
            cursor.execute("DELETE FROM notificaciones WHERE id_resena_ref=%s", (res[0],))
            cursor.execute("DELETE FROM resena WHERE id_resena=%s", (res[0],))
        else:
            cursor.execute(
                "DELETE FROM notificaciones WHERE id_notificacion=%s AND id_usuario_receptor=%s",
                (notification_id, user_id)
            )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500