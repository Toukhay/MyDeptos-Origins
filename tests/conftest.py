import pytest
from app import create_app
from extensions import db as _db
from models import Localidad


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    return app


@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        _db.create_all()
        localidades = ['Posadas', 'Oberá', 'Eldorado']
        for nombre in localidades:
            _db.session.add(Localidad(nombre=nombre))
        _db.session.commit()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def auth_client(app, db):
    from werkzeug.security import generate_password_hash
    from models import Usuario
    with app.app_context():
        existing = Usuario.query.filter_by(name='testuser').first()
        if not existing:
            user = Usuario(
                name='testuser',
                email='test@test.com',
                password=generate_password_hash('password123'),
                telefono='3764000000',
                rol='user'
            )
            _db.session.add(user)
            _db.session.commit()

    client = app.test_client()
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    return client