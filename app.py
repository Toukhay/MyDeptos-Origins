import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, session
from flask_login import current_user

from config import Config
from extensions import db, login_manager, csrf, migrate


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    Config.validate()

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Configurar logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/mydeptos.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MyDeptos iniciado')

    # Importar modelos para que Alembic los detecte
    from models import (Usuario, Localidad, Departamento, Foto,
                        Coordenada, Favorito, Resena, Notificacion,
                        ConfiguracionUsuario)

    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.deptos import deptos_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(deptos_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # Context processor
    @app.context_processor
    def inject_globals():
        unread = 0
        if 'user_id' in session:
            try:
                from models import Notificacion
                unread = Notificacion.query.filter_by(
                    id_usuario_receptor=session['user_id'],
                    leida=False
                ).count()
            except Exception:
                unread = 0
        return dict(current_user=current_user, unread_notification_count=unread)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)